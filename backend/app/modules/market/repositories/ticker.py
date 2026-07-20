from datetime import UTC, datetime

from sqlalchemy import case, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.market.models import Ticker


class TickerRepository(BaseRepository[Ticker]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Ticker, session)

    async def get_all_by_market(self, market: str) -> list[Ticker]:
        return await self.get_all(self.model.market == market)

    async def update_ticker_prices(self, data: dict[str, object]) -> int:
        if not data:
            return 0
        now = datetime.now(UTC)
        ids = list(data.keys())
        value_mappings = [(self.model.id == id, value) for id, value in data.items()]
        case_expr = case(*value_mappings, else_=self.model.price)
        stmt = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(price=case_expr, updated_at=now)
            .execution_options(synchronize_session=False)
        )
        result = await self._session.execute(stmt)
        return result.rowcount
