import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.market.repositories.ticker_identifier import TickerIdentifierRepository

logger = logging.getLogger(__name__)


class TickerIdentifierService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TickerIdentifierRepository(session)

    async def find_matching_ticker(self, identifiers: dict[str, str], market: str) -> int | None:
        if not identifiers:
            return None
        existing = await self.repo.find_by_identifiers(identifiers)
        if not existing:
            return None
        ticker_ids = set(ti.ticker_id for ti in existing.values())
        if len(ticker_ids) > 1:
            logger.warning('Identifiers %s resolve to multiple tickers: %s', identifiers, ticker_ids)
        return ticker_ids.pop()

    async def save_identifiers(self, ticker_id: int, identifiers: dict[str, str]) -> None:
        await self.repo.upsert_all(ticker_id, identifiers)
