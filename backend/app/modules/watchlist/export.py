from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exporting import fetch_all, model_rows
from app.modules.auth.protocols import ExportAccumulator, UserDataCollector
from app.modules.watchlist.models import PriceAlert, WatchlistItem


class WatchlistDataCollector(UserDataCollector):
    """Разделы избранного и ценовых алертов."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def collect(self, user_id: int, acc: ExportAccumulator) -> None:
        items = await fetch_all(self._session, WatchlistItem, WatchlistItem.user_id == user_id)
        alerts = await fetch_all(self._session, PriceAlert, PriceAlert.user_id == user_id)
        acc.sections['watchlist_items'] = model_rows(items)
        acc.sections['price_alerts'] = model_rows(alerts)
