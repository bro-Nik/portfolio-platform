from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from app.common.schemas import Context
from app.common.utils.decimal import clean_decimal
from app.modules.portfolios.models import Transaction, WalletAsset
from app.modules.portfolios.repositories import (
    TransactionRepository,
    WalletAssetRepository,
)
from app.modules.portfolios.services.transaction_analyzer import combine_ids_and_tickers


class WalletAssetService:
    def __init__(self, ctx: Context, session: AsyncSession) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = WalletAssetRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def get(self, id: int) -> WalletAsset:
        asset = await self.repo.get(id)
        self._verify(asset)
        return asset

    async def delete(self, id: int) -> bool:
        asset = await self.get(id)
        has_txns = await self.transaction_repo.exists_for_wallet_ticker(asset.wallet_id, asset.ticker_id)
        if has_txns:
            raise ConflictError('Нельзя удалить актив с транзакциями')
        return bool(await self.repo.delete(id))

    async def archive(self, id: int) -> None:
        await self.get(id)
        await self.repo.update(id, {'is_archived': True})

    async def archive_many(self, ids: list[int]) -> None:
        if ids:
            await self.repo.update_all_by_ids(ids, {'is_archived': True})

    async def unarchive(self, id: int) -> None:
        await self.get(id)
        await self.repo.update(id, {'is_archived': False})

    async def handle_transaction(self, t: Transaction, *, cancel: bool = False) -> None:
        direction = t.get_direction(cancel=cancel)
        if t.type in ('Buy', 'Sell'):
            await self._handle_trade(t, direction)
        elif t.type == 'Earning':
            await self._handle_earning(t, direction)
        elif t.type in ('TransferIn', 'TransferOut'):
            await self._handle_transfer(t, direction)
        elif t.type in ('Input', 'Output'):
            await self._handle_input_output(t, direction)

    async def get_transactions(self, id: int) -> list[Transaction]:
        asset = await self.get(id)
        return await self.transaction_repo.get_all_by_ticker_and_wallet(asset.ticker_id, asset.wallet_id)

    async def get_distribution(self, id: int) -> dict:
        asset = await self.get(id)
        assets = await self.repo.get_all_by_ticker_and_user_with_wallets(asset.ticker_id, self.actor.id)
        total_qty = sum(a.quantity for a in assets)
        distribution = [{
            'wallet_id': a.wallet.id, 'wallet_name': a.wallet.name,
            'quantity': a.quantity,
            'percentage_of_total': round(float(a.quantity / total_qty * 100) if total_qty > 0 else 0, 2),
        } for a in assets]
        return {'total_quantity_all_wallets': total_qty, 'wallets': distribution}

    async def get_affected(self, *transactions: Transaction) -> list[WalletAsset]:
        pairs = {
            pair for t in transactions
            for pair in combine_ids_and_tickers(
                [t.wallet_id, t.wallet2_id],
                [t.ticker_id, t.ticker2_id],
            )
        }
        if not pairs:
            return []
        assets_map = defaultdict(list)
        for wallet_id, ticker_id in pairs:
            assets_map[wallet_id].append(ticker_id)
        return await self.repo.get_all_by_wallet_tickers(assets_map)

    async def _get_or_create(self, *pairs: tuple) -> tuple:
        valid = [(w_id, t_id) for w_id, t_id in pairs if w_id is not None and t_id is not None]
        if not valid:
            return ()
        assets_map = defaultdict(list)
        for w_id, t_id in valid:
            assets_map[w_id].append(t_id)
        existing = await self.repo.get_all_by_wallet_tickers(assets_map)
        existing_by_pair = {(a.wallet_id, a.ticker_id): a for a in existing}
        missing = [pair for pair in valid if pair not in existing_by_pair]
        created = await self.repo.create_all([
            {'wallet_id': w_id, 'ticker_id': t_id, 'user_id': self.actor.id}
            for w_id, t_id in missing
        ])
        created_by_pair = {(a.wallet_id, a.ticker_id): a for a in created}
        await self.session.flush()
        return tuple(existing_by_pair.get(pair) or created_by_pair[pair] for pair in valid)

    async def _handle_trade(self, t: Transaction, direction: int) -> None:
        a1, a2 = await self._get_or_create((t.wallet_id, t.ticker_id), (t.wallet_id, t.ticker2_id))
        handler = self._handle_trade_order if t.order else self._handle_trade_execution
        handler(a1, t, direction, is_base_asset=True)
        handler(a2, t, direction, is_base_asset=False)
        self._clean_asset(a1)
        self._clean_asset(a2)

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
        self._clean_asset(asset)

    async def _handle_transfer(self, t: Transaction, direction: int) -> None:
        a1, a2 = await self._get_or_create((t.wallet_id, t.ticker_id), (t.wallet2_id, t.ticker_id))
        qty = t.quantity * direction
        a1.quantity += qty
        a2.quantity -= qty
        self._clean_asset(a1)
        self._clean_asset(a2)

    async def _handle_input_output(self, t: Transaction, direction: int) -> None:
        (asset,) = await self._get_or_create((t.wallet_id, t.ticker_id))
        asset.quantity += t.quantity * direction
        self._clean_asset(asset)

    def _clean_asset(self, asset: WalletAsset) -> None:
        for field in ('quantity', 'buy_orders', 'sell_orders'):
            setattr(asset, field, clean_decimal(getattr(asset, field)))

    def _verify(self, asset) -> None:
        if not asset:
            raise NotFoundError('Актив не найден')
        if asset.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав для получения актива')
