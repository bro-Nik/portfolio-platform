from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.market.models import Ticker
from app.modules.portfolios.models import PortfolioAsset, Transaction, WalletAsset


class TickerUsageRepository:
    """Реализация market.protocols.TickerUsageReader на таблицах portfolios."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_used_ticker_ids(self, market: str | None = None) -> list[int]:
        portfolio_ids = select(PortfolioAsset.ticker_id).distinct()
        wallet_ids = select(WalletAsset.ticker_id).distinct()
        if market:
            portfolio_ids = portfolio_ids.join(
                Ticker,
                Ticker.id == PortfolioAsset.ticker_id,
            ).where(Ticker.market == market)
            wallet_ids = wallet_ids.join(
                Ticker,
                Ticker.id == WalletAsset.ticker_id,
            ).where(Ticker.market == market)
        result = await self._session.execute(portfolio_ids.union(wallet_ids))
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
