from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.repositories import BaseRepository
from app.modules.market.models import Ticker
from app.modules.market.protocols import TickerUsageReader
from app.modules.watchlist.models import PriceAlert, WatchlistItem


class WatchlistItemRepository(BaseRepository[WatchlistItem]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(WatchlistItem, session)

    async def get_by_user(self, user_id: int) -> list[WatchlistItem]:
        return await self.get_all(
            self.model.user_id == user_id,
            order=[self.model.created_at.asc()],
            relations=('alerts',),
        )

    async def get_own(self, item_id: int, user_id: int) -> WatchlistItem | None:
        return await self.get_by(
            self.model.id == item_id,
            self.model.user_id == user_id,
            relations=('alerts',),
        )

    async def exists_for_user(self, user_id: int, ticker_id: int) -> bool:
        return await self._exists(
            self.model.user_id == user_id,
            self.model.ticker_id == ticker_id,
        )


class PriceAlertRepository(BaseRepository[PriceAlert]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PriceAlert, session)

    async def get_own(self, alert_id: int, user_id: int) -> PriceAlert | None:
        return await self.get_by(
            self.model.id == alert_id,
            self.model.user_id == user_id,
        )

    async def get_active_by_ticker_ids(self, ticker_ids: list[int]) -> list[PriceAlert]:
        """Активные алерты по только что обновлённым тикерам — один запрос, без N+1."""
        if not ticker_ids:
            return []
        result = await self._session.execute(
            select(self.model)
            .join(WatchlistItem, WatchlistItem.id == self.model.watchlist_item_id)
            .where(
                WatchlistItem.ticker_id.in_(ticker_ids),
                WatchlistItem.is_archived.is_(False),
                self.model.is_active.is_(True),
                self.model.is_archived.is_(False),
            )
            .options(selectinload(self.model.watchlist_item))
        )
        return list(result.scalars().all())

    async def get_triggered_by_user(self, user_id: int) -> list[PriceAlert]:
        return await self.get_all(
            self.model.user_id == user_id,
            self.model.is_active.is_(False),
            self.model.triggered_at.is_not(None),
            self.model.is_archived.is_(False),
            order=[self.model.triggered_at.desc()],
            relations=('watchlist_item',),
        )


class WatchlistUsageRepository(TickerUsageReader):
    """Вклад избранного в market.protocols.TickerUsageReader.

    Живёт в watchlist (владеет таблицей), объединяется с реализацией portfolios
    в композите app.di.UnionTickerUsageRepository — ни один модуль не импортирует
    другой напрямую.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_used_ticker_ids(self, market: str | None = None) -> list[int]:
        stmt = select(WatchlistItem.ticker_id).distinct().where(WatchlistItem.is_archived.is_(False))
        if market:
            stmt = stmt.join(Ticker, Ticker.id == WatchlistItem.ticker_id).where(Ticker.market == market)
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all() if row[0]]

    async def count_references(self, ticker_id: int) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(WatchlistItem).where(WatchlistItem.ticker_id == ticker_id)
        )
        return result.scalar_one()

    async def reassign_references(self, source_id: int, target_id: int) -> None:
        await self._session.execute(
            update(WatchlistItem).where(WatchlistItem.ticker_id == source_id).values(ticker_id=target_id)
        )
