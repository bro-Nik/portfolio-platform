from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.portfolios.models import PortfolioAsset, Transaction, WalletAsset


class TickerUsageRepository:
    """Реализация market.protocols.TickerUsageReader на таблицах portfolios."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_used_ticker_ids(self) -> list[int]:
        result = await self._session.execute(
            select(PortfolioAsset.ticker_id)
            .distinct()
            .union(
                select(WalletAsset.ticker_id).distinct(),
            ),
        )
        return [row[0] for row in result.all() if row[0]]

    async def count_references(self, ticker_id: int) -> int:
        statements = [
            select(func.count()).select_from(PortfolioAsset).where(PortfolioAsset.ticker_id == ticker_id),
            select(func.count()).select_from(WalletAsset).where(WalletAsset.ticker_id == ticker_id),
            select(func.count()).select_from(Transaction).where(Transaction.ticker_id == ticker_id),
            select(func.count()).select_from(Transaction).where(Transaction.ticker2_id == ticker_id),
        ]
        total = 0
        for statement in statements:
            total += (await self._session.execute(statement)).scalar_one()
        return total

    async def reassign_references(self, source_id: int, target_id: int) -> None:
        statements = [
            update(PortfolioAsset).where(PortfolioAsset.ticker_id == source_id).values(ticker_id=target_id),
            update(WalletAsset).where(WalletAsset.ticker_id == source_id).values(ticker_id=target_id),
            update(Transaction).where(Transaction.ticker_id == source_id).values(ticker_id=target_id),
            update(Transaction).where(Transaction.ticker2_id == source_id).values(ticker2_id=target_id),
        ]
        for statement in statements:
            await self._session.execute(statement)
