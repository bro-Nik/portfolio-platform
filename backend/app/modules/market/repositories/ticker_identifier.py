from sqlalchemy import and_, or_, select
from sqlalchemy.dialects.postgresql import insert
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
            and_(self.model.system == system, self.model.value == value) for system, value in identifiers.items()
        ]
        rows = await self.get_all(or_(*conditions))
        return {row.system: row for row in rows}

    async def find_ticker_ids_by_pairs(self, pairs: set[tuple[str, str]]) -> dict[tuple[str, str], int]:
        """Все совпадения (system, value) -> ticker_id одним запросом.

        По одному запросу на тикер синхронизация провайдера давала тысячи
        round-trip'ов; здесь дизъюнктов по-прежнему много, но запрос один.
        """
        if not pairs:
            return {}
        stmt = select(self.model.system, self.model.value, self.model.ticker_id).where(
            or_(*(and_(self.model.system == system, self.model.value == value) for system, value in pairs)),
        )
        rows = await self._session.execute(stmt)
        return {(system, value): ticker_id for system, value, ticker_id in rows}

    async def upsert_all(self, ticker_id: int, identifiers: dict[str, str]) -> None:
        await self.insert_many(
            [{'ticker_id': ticker_id, 'system': system, 'value': value} for system, value in identifiers.items()],
        )

    async def insert_many(self, rows: list[dict]) -> int:
        """Массовая вставка с игнорированием уже существующих (system, value).

        Поведение совпадает с прежней построчной версией: пара (system, value)
        принадлежит первому тикеру, который её заявил, и не переназначается.
        """
        if not rows:
            return 0
        deduped = {row['value']: row for row in rows}
        stmt = (
            insert(self.model)
            .values(list(deduped.values()))
            .on_conflict_do_nothing(index_elements=[self.model.system, self.model.value])
        )
        await self._session.execute(stmt)
        return len(deduped)
