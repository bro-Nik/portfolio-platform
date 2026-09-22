import logging

from app.modules.market.models import TickerIdentifier
from app.modules.market.repositories import TickerIdentifierRepository

logger = logging.getLogger(__name__)


class TickerIdentifierService:
    def __init__(self, repo: TickerIdentifierRepository) -> None:
        self.repo = repo

    async def find_matching_ticker(self, identifiers: dict[str, str], market: str) -> int | None:
        if not identifiers:
            return None
        existing = await self.repo.find_by_identifiers(identifiers)
        if not existing:
            return None
        return self._pick_ticker_id(existing, identifiers)

    def find_matching_ticker_in_map(
        self,
        identifiers: dict[str, str],
        known: dict[tuple[str, str], int],
    ) -> int | None:
        """Совпадение по предзагруженной карте пар (без запроса в БД)."""
        if not identifiers:
            return None
        matched = {known[(system, value)] for system, value in identifiers.items() if (system, value) in known}
        if not matched:
            return None
        if len(matched) > 1:
            logger.warning('Identifiers %s resolve to multiple tickers: %s', identifiers, matched)
        return matched.pop()

    async def load_ticker_ids(self, pairs: set[tuple[str, str]]) -> dict[tuple[str, str], int]:
        return await self.repo.find_ticker_ids_by_pairs(pairs)

    async def save_identifiers(self, ticker_id: int, identifiers: dict[str, str]) -> None:
        await self.repo.upsert_all(ticker_id, identifiers)

    async def save_identifiers_many(self, rows: list[dict]) -> int:
        return await self.repo.insert_many(rows)

    @staticmethod
    def _pick_ticker_id(
        existing: dict[str, TickerIdentifier],
        identifiers: dict[str, str],
    ) -> int | None:
        ticker_ids = {ti.ticker_id for ti in existing.values()}
        if len(ticker_ids) > 1:
            logger.warning('Identifiers %s resolve to multiple tickers: %s', identifiers, ticker_ids)
        return ticker_ids.pop()
