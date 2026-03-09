import asyncio
from collections import defaultdict

from shared.exceptions import NotFoundError, PermissionDeniedError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Transaction, WalletAsset
from app.repositories import TransactionRepository, WalletAssetRepository
from app.schemas import Context


class WalletAssetService:
    """Сервис для работы с активами кошельков."""

    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = WalletAssetRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def get(self, id: int) -> WalletAsset:
        """Получить актив пользователя."""
        asset = await self.repo.get(id)
        self._verify(asset)
        return asset

    async def handle_transaction(self, t: Transaction, *, cancel: bool = False) -> None:
        """Обработка транзакции."""
        direction = t.get_direction(cancel)

        if t.type in ('Buy', 'Sell'):
            await self._handle_trade(t, direction)
        elif t.type == 'Earning':
            await self._handle_earning(t, direction)
        elif t.type in ('TransferIn', 'TransferOut'):
            await self._handle_transfer(t, direction)
        elif t.type in ('Input', 'Output'):
            await self._handle_input_output(t, direction)

    async def get_transactions(self, id: int) -> list[Transaction]:
        """Получение транзакций актива."""
        asset = await self.get(id)
        return await self.transaction_repo.get_many_by_ticker_and_wallet(asset.ticker_id, asset.wallet_id)

    async def get_distribution(self, id: int) -> dict:
        """Получение информации о распределении актива по кошелькам."""
        asset = await self.get(id)
        assets = await self.repo.get_many_by_ticker_and_user_with_wallets(asset.ticker_id, self.actor.id)

        total_quantity = sum(asset.quantity for asset in assets)

        distribution = []
        for asset in assets:
            percentage = (asset.quantity / total_quantity * 100) if total_quantity > 0 else 0
            distribution.append(
                {
                    'wallet_id': asset.wallet.id,
                    'wallet_name': asset.wallet.name,
                    'quantity': asset.quantity,
                    'percentage_of_total': round(float(percentage), 2),
                }
            )

        return {
            'total_quantity_all_wallets': total_quantity,
            'wallets': distribution,
        }

    async def get_affected(self, *transactions: Transaction) -> list[WalletAsset]:
        """Получить измененные активы кошельков на основе транзакций."""
        from app.services.transaction_analyzer import get_wallet_pairs as get_pairs

        # Сбор затронутых пар (wallet_id, ticker_id)
        pairs = {pair for t in transactions for pair in get_pairs(t)}
        if not pairs:
            return []

        # Группировка по wallet_id
        assets_map = defaultdict(list)
        for wallet_id, ticker_id in pairs:
            assets_map[wallet_id].append(ticker_id)

        # Получение активов для каждого кошелька
        results = await asyncio.gather(*[
            self.repo.get_many_by_tickers_and_wallet(ticker_ids, wallet_id)
            for wallet_id, ticker_ids in assets_map.items()
        ])

        return [asset for result in results for asset in result]

    async def _get_or_create(self, *pairs: tuple) -> tuple[WalletAsset, ...]:
        results = await asyncio.gather(*[
            self.repo.get_or_create(wallet_id=w_id, ticker_id=t_id, user_id=self.actor.id)
            for w_id, t_id in pairs
            if w_id is not None and t_id is not None
        ])
        await self.session.flush()
        return tuple(results)

    async def _handle_trade(self, t: Transaction, direction: int) -> None:
        asset1, asset2 = await self._get_or_create(
            (t.wallet_id, t.ticker_id), (t.wallet_id, t.ticker2_id),
        )

        handler = self._handle_trade_order if t.order else self._handle_trade_execution
        handler(asset1, t, direction, is_base_asset=True)
        handler(asset2, t, direction, is_base_asset=False)

    def _handle_trade_execution(self, asset: WalletAsset, t: Transaction, direction: int, *, is_base_asset: bool) -> None:
        if is_base_asset:
            asset.quantity += t.quantity * direction
        elif not is_base_asset:
            asset.quantity -= t.quantity2 * direction

    def _handle_trade_order(self, asset: WalletAsset, t: Transaction, direction: int, *, is_base_asset: bool) -> None:
        if is_base_asset:
            if t.type == 'Buy':
                asset.buy_orders += t.quantity * t.price_usd * direction
            elif t.type == 'Sell':
                asset.sell_orders -= t.quantity * direction
        elif not is_base_asset and t.type == 'Buy':
            asset.sell_orders -= t.quantity2 * direction

    async def _handle_earning(self, t: Transaction, direction: int) -> None:
        (asset,) = await self._get_or_create((t.wallet_id, t.ticker_id))
        asset.quantity += t.quantity * direction

    async def _handle_transfer(self, t: Transaction, direction: int) -> None:
        asset1, asset2 = await self._get_or_create(
            (t.wallet_id, t.ticker_id), (t.wallet2_id, t.ticker_id),
        )

        quantity = t.quantity * direction
        asset1.quantity += quantity
        asset2.quantity -= quantity

    async def _handle_input_output(self, t: Transaction, direction: int) -> None:
        (asset,) = await self._get_or_create((t.wallet_id, t.ticker_id))
        asset.quantity += t.quantity * direction

    def _verify(self, asset: WalletAsset) -> None:
        self._check_exists(asset)
        self._check_permission(asset)

    def _check_exists(self, asset: WalletAsset | None) -> None:
        if not asset:
            raise NotFoundError('Актив не найден')

    def _check_permission(self, asset: WalletAsset) -> None:
        if asset.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав для получения актива')
