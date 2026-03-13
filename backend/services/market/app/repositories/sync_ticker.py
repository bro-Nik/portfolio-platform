from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models import Ticker
from app.repositories import BaseSyncRepository


class SyncTickerRepository(BaseSyncRepository[Ticker, None, None]):
    """Репозиторий для работы с тикерами."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def update_ticker_prices(self, data: dict[int, float]) -> int:
        """Обновить цены тикеров."""
        now = datetime.now(UTC)
        return self.update_many_with_map(data, 'price', add_values={'updated_at': now})
