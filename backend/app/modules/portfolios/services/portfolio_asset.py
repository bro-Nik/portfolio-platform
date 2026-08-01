from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictError, NotFoundError, PermissionDeniedError

from app.modules.portfolios.models import PortfolioAsset, Transaction
from app.modules.portfolios.repositories import (
    PortfolioAssetRepository, TransactionRepository,
)
from app.modules.portfolios.schemas import (
    PortfolioAssetCreate, PortfolioAssetCreateRequest,
)
from app.common.schemas import Context

from app.modules.portfolios.services.transaction_analyzer import combine_ids_and_tickers


class PortfolioAssetService:
    def __init__(self, ctx: Context, session: AsyncSession) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = PortfolioAssetRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def get(self, id: int) -> PortfolioAsset:
        asset = await self.repo.get(id)
        self._verify(asset)
        return asset

    async def create(self, data: PortfolioAssetCreateRequest) -> PortfolioAsset:
        if await self.repo.get_by_ticker_and_portfolio(data.ticker_id, data.portfolio_id):
            raise ConflictError('Этот актив уже добавлен в портфель')
        asset = await self.repo.create(PortfolioAssetCreate(**data.model_dump(), user_id=self.actor.id).model_dump())
        await self.session.flush()
        return asset

    async def delete(self, id: int) -> bool:
        asset = await self.get(id)
        has_txns = await self.transaction_repo.exists_for_portfolio_ticker(asset.portfolio_id, asset.ticker_id)
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
        asset = await self.get(id)
        return await self.transaction_repo.get_all_by_ticker_and_portfolio(asset.ticker_id, asset.portfolio_id)

    async def get_distribution(self, id: int) -> dict:
        asset = await self.get(id)
        assets = await self.repo.get_all_by_ticker_and_user_with_portfolios(asset.ticker_id, self.actor.id)
        total_qty = sum(a.quantity for a in assets)
        total_amt = sum(a.amount for a in assets)
        distribution = [{
            'portfolio_id': a.portfolio.id, 'portfolio_name': a.portfolio.name,
            'quantity': a.quantity, 'amount': a.amount,
            'percentage_of_total': round(float(a.quantity / total_qty * 100) if total_qty > 0 else 0, 2),
        } for a in assets]
        return {'total_quantity_all_portfolios': total_qty, 'total_amount_all_portfolios': total_amt, 'portfolios': distribution}

    async def get_affected(self, *transactions: Transaction) -> list[PortfolioAsset]:
        pairs = {
            pair for t in transactions
            for pair in combine_ids_and_tickers(
                [t.portfolio_id, t.portfolio2_id],
                [t.ticker_id, t.ticker2_id],
            )
        }
        if not pairs:
            return []
        assets_map = defaultdict(list)
        for portfolio_id, ticker_id in pairs:
            assets_map[portfolio_id].append(ticker_id)
        return await self.repo.get_all_by_portfolio_tickers(assets_map)

    async def _get_or_create(self, *pairs: tuple) -> tuple:
        valid = [(p_id, t_id) for p_id, t_id in pairs if p_id is not None and t_id is not None]
        if not valid:
            return ()
        assets_map = defaultdict(list)
        for p_id, t_id in valid:
            assets_map[p_id].append(t_id)
        existing = await self.repo.get_all_by_portfolio_tickers(assets_map)
        existing_by_pair = {(a.portfolio_id, a.ticker_id): a for a in existing}
        missing = [pair for pair in valid if pair not in existing_by_pair]
        created = await self.repo.create_all([
            {'portfolio_id': p_id, 'ticker_id': t_id, 'user_id': self.actor.id}
            for p_id, t_id in missing
        ])
        created_by_pair = {(a.portfolio_id, a.ticker_id): a for a in created}
        await self.session.flush()
        return tuple(existing_by_pair.get(pair) or created_by_pair[pair] for pair in valid)

    async def _handle_trade(self, t: Transaction, direction: int) -> None:
        a1, a2 = await self._get_or_create((t.portfolio_id, t.ticker_id), (t.portfolio_id, t.ticker2_id))
        handler = self._handle_trade_order if t.order else self._handle_trade_execution
        handler(a1, t, direction, is_base_asset=True)
        handler(a2, t, direction, is_base_asset=False)

    def _handle_trade_execution(self, asset: PortfolioAsset, t: Transaction, direction: int, *, is_base_asset: bool) -> None:
        if is_base_asset:
            if direction > 0:
                asset.quantity += t.quantity
                asset.amount += t.quantity * t.price_usd
                asset.total_invested += t.quantity * t.price_usd
            else:
                if asset.quantity > 0:
                    avg = asset.amount / asset.quantity
                    asset.amount -= t.quantity * avg
                    asset.realized_profit += t.quantity * (t.price_usd - avg)
                asset.quantity -= t.quantity
        elif not is_base_asset:
            asset.quantity -= t.quantity2 * direction

    def _handle_trade_order(self, asset: PortfolioAsset, t: Transaction, direction: int, *, is_base_asset: bool) -> None:
        if is_base_asset:
            if t.type == 'Buy':
                asset.buy_orders += t.quantity * t.price_usd * direction
            elif t.type == 'Sell':
                asset.sell_orders -= t.quantity * direction
        elif not is_base_asset and t.type == 'Buy':
            asset.sell_orders -= t.quantity2 * direction

    async def _handle_earning(self, t: Transaction, direction: int) -> None:
        (asset,) = await self._get_or_create((t.portfolio_id, t.ticker_id))
        asset.quantity += t.quantity * direction

    async def _handle_transfer(self, t: Transaction, direction: int) -> None:
        a1, a2 = await self._get_or_create((t.portfolio_id, t.ticker_id), (t.portfolio2_id, t.ticker_id))
        if a1.quantity and t.quantity:
            a1.amount += a1.amount / a1.quantity * t.quantity * direction
            a2.amount -= a1.amount / a1.quantity * t.quantity * direction
        qty = t.quantity * direction
        a1.quantity += qty
        a2.quantity -= qty

    async def _handle_input_output(self, t: Transaction, direction: int) -> None:
        (asset,) = await self._get_or_create((t.portfolio_id, t.ticker_id))
        asset.quantity += t.quantity * direction

    def _verify(self, asset) -> None:
        if not asset:
            raise NotFoundError('Актив не найден')
        if asset.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав для получения актива')
