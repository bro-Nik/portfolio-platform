from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository
from app.modules.market.models import Ticker, TickerExternalId


class TickerExternalIdRepository(BaseRepository[TickerExternalId]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TickerExternalId, session)

    async def get_ext_id_map(self, ticker_ids: list[int], provider_name: str) -> dict[int, str]:
        if not ticker_ids:
            return {}
        rows = await self.get_all(
            self.model.ticker_id.in_(ticker_ids),
            self.model.provider_name == provider_name,
        )
        return {row.ticker_id: row.external_id for row in rows}

    async def get_ticker_id_map(self, provider_name: str, ext_ids: list[str]) -> dict[str, int]:
        if not ext_ids:
            return {}
        rows = await self.get_all(
            self.model.external_id.in_(ext_ids),
            self.model.provider_name == provider_name,
        )
        return {row.external_id: row.ticker_id for row in rows}

    async def get_ext_to_ticker_map(self, provider_name: str) -> dict[str, int]:
        rows = await self.get_all(self.model.provider_name == provider_name)
        return {row.external_id: row.ticker_id for row in rows}

    async def upsert(self, ticker_id: int, provider_name: str, ext_id: str) -> TickerExternalId:
        obj = self.model(
            ticker_id=ticker_id,
            provider_name=provider_name,
            external_id=ext_id,
        )
        return await self._session.merge(obj)

    async def find_tickers_without_ext_id(self, provider_name: str) -> list[Ticker]:
        subq = select(self.model.ticker_id).where(
            self.model.provider_name == provider_name,
            self.model.ticker_id == Ticker.id,
        )
        stmt = select(Ticker).where(Ticker.market == 'crypto', ~exists(subq))
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
