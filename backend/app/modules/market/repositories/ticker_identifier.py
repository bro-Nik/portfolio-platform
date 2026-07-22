from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository
from app.modules.market.models import TickerIdentifier


class TickerIdentifierRepository(BaseRepository[TickerIdentifier]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(TickerIdentifier, session)

    async def find_by_system_value(self, system: str, value: str) -> TickerIdentifier | None:
        return await self.get_by(
            self.model.system == system,
            self.model.value == value,
        )

    async def find_by_identifiers(self, identifiers: dict[str, str]) -> dict[str, TickerIdentifier]:
        if not identifiers:
            return {}
        conditions = [
            and_(self.model.system == system, self.model.value == value)
            for system, value in identifiers.items()
        ]
        rows = await self.get_all(or_(*conditions))
        return {row.system: row for row in rows}

    async def upsert(self, ticker_id: int, system: str, value: str) -> TickerIdentifier:
        existing = await self.get_by(
            self.model.system == system,
            self.model.value == value,
        )
        if existing:
            return existing
        return await self.create({
            'ticker_id': ticker_id,
            'system': system,
            'value': value,
        })

    async def upsert_all(self, ticker_id: int, identifiers: dict[str, str]) -> None:
        for system, value in identifiers.items():
            await self.upsert(ticker_id, system, value)
