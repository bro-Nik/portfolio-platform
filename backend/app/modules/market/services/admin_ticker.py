import logging

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BusinessRuleError, NotFoundError
from app.modules.market.models import Ticker, TickerExternalId, TickerIdentifier
from app.modules.market.repositories import TickerRepository
from app.modules.market.schemas import TickerAdminResponse, TickerUpdateRequest

logger = logging.getLogger(__name__)


class TickerAdminService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TickerRepository(session)

    async def list(self, search: str | None = None, market: str | None = None,
                   page: int = 1, page_size: int = 20) -> dict:
        from sqlalchemy import func, or_, select

        query = select(Ticker)
        count_query = select(func.count()).select_from(Ticker)
        where = []
        if search:
            term = f'%{search}%'
            where.append(or_(Ticker.name.ilike(term), Ticker.symbol.ilike(term)))
        if market:
            where.append(Ticker.market == market)
        if where:
            query = query.where(*where)
            count_query = count_query.where(*where)
        total = (await self.session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        query = query.order_by(
            Ticker.market_cap_rank.asc().nulls_last(), Ticker.symbol.asc()
        ).offset(offset).limit(page_size + 1)
        tickers = (await self.session.execute(query)).scalars().all()
        has_more = len(tickers) > page_size
        if has_more:
            tickers = tickers[:-1]
        return {
            'data': [TickerAdminResponse.model_validate(t) for t in tickers],
            'has_more': has_more,
            'total': total,
        }

    async def get_by_id(self, ticker_id: int) -> TickerAdminResponse:
        ticker = await self.repo.get(ticker_id, relations=['external_ids', 'identifiers'])
        if not ticker:
            raise NotFoundError('Тикер не найден')
        return TickerAdminResponse.model_validate(ticker)

    async def update(self, ticker_id: int, data: TickerUpdateRequest) -> Ticker:
        ticker = await self.repo.get(ticker_id)
        if not ticker:
            raise NotFoundError('Тикер не найден')
        dump = data.model_dump(exclude_unset=True)
        if not dump:
            raise BusinessRuleError('Нет полей для обновления')
        return await self.repo.update(ticker_id, dump)

    async def delete(self, ticker_id: int) -> None:
        ticker = await self.repo.get(ticker_id)
        if not ticker:
            raise NotFoundError('Тикер не найден')

        refs = await self._count_references(ticker_id)
        if refs > 0:
            raise BusinessRuleError(
                f'Тикер используется в {refs} записях. Удалите или переназначьте их перед удалением.'
            )

        await self.repo.delete(ticker_id)

    async def merge(self, source_id: int, target_id: int) -> Ticker:
        if source_id == target_id:
            raise BusinessRuleError('Нельзя объединить тикер с самим собой')

        source = await self.repo.get(source_id)
        target = await self.repo.get(target_id)
        if not source or not target:
            raise NotFoundError('Один из тикеров не найден')

        await self._merge_reassign_external_ids(source_id, target_id)
        await self._merge_reassign_identifiers(source_id, target_id)
        await self._merge_update_references(source_id, target_id)

        await self.repo.delete(source_id)
        await self.session.flush()

        merged = await self.repo.get(target_id, relations=['external_ids', 'identifiers'])
        return TickerAdminResponse.model_validate(merged)

    async def _count_references(self, ticker_id: int) -> int:
        result = await self.session.execute(text("""
            SELECT
                (SELECT COUNT(*) FROM portfolio_asset WHERE ticker_id = :id) +
                (SELECT COUNT(*) FROM wallet_asset WHERE ticker_id = :id) +
                (SELECT COUNT(*) FROM "transaction" WHERE ticker_id = :id) +
                (SELECT COUNT(*) FROM "transaction" WHERE ticker2_id = :id)
        """), {'id': ticker_id})
        return result.scalar() or 0

    async def _merge_update_references(self, source_id: int, target_id: int) -> None:
        tables = [
            ('portfolio_asset', 'ticker_id'),
            ('wallet_asset', 'ticker_id'),
            ('"transaction"', 'ticker_id'),
            ('"transaction"', 'ticker2_id'),
        ]
        for table, column in tables:
            await self.session.execute(
                text(f'UPDATE {table} SET {column} = :target WHERE {column} = :source'),
                {'source': source_id, 'target': target_id},
            )

    async def _merge_reassign_external_ids(self, source_id: int, target_id: int) -> None:
        existing = await self.session.execute(
            select(TickerExternalId.provider_name).where(TickerExternalId.ticker_id == target_id)
        )
        target_providers = {row[0] for row in existing}

        rows = await self.session.execute(
            select(TickerExternalId).where(TickerExternalId.ticker_id == source_id)
        )
        for row in rows.scalars():
            if row.provider_name not in target_providers:
                row.ticker_id = target_id
            else:
                await self.session.delete(row)

    async def _merge_reassign_identifiers(self, source_id: int, target_id: int) -> None:
        existing = await self.session.execute(
            select(TickerIdentifier.system, TickerIdentifier.value).where(
                TickerIdentifier.ticker_id == target_id
            )
        )
        target_keys = {(row.system, row.value) for row in existing}

        rows = await self.session.execute(
            select(TickerIdentifier).where(TickerIdentifier.ticker_id == source_id)
        )
        for row in rows.scalars():
            key = (row.system, row.value)
            if key not in target_keys:
                row.ticker_id = target_id
            else:
                await self.session.delete(row)
