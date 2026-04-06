from datetime import UTC, datetime

from sqlalchemy import case, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Ticker
from app.repositories import BaseRepository

Id = int | str


class TickerRepository(BaseRepository[Ticker, None, None]):
    """Репозиторий для работы с тикерами."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Ticker, session)

    async def update_ticker_prices(self, data: dict[Id, object]) -> int:
        """Обновить цены тикеров."""
        if not data:
            return 0

        now = datetime.now(UTC)
        ids = list(data.keys())
        value_mappings = [(self.model.id == id, value) for id, value in data.items()]

        case_expr = case(*value_mappings, else_=self.model.price)
        values = {'price': case_expr, 'updated_at': now}

        stmt = (
            update(self.model)
            .where(self.model.id.in_(ids))
            .values(**values)
            .execution_options(synchronize_session=False)
        )

        result = await self.session.execute(stmt)
        return result.rowcount
