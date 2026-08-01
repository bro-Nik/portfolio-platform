from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository
from app.modules.portfolios.models import PortfolioAsset


class PortfolioAssetRepository(BaseRepository[PortfolioAsset]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PortfolioAsset, session)

    async def get_by_ticker_and_portfolio(self, ticker_id: int, portfolio_id: int) -> PortfolioAsset | None:
        return await self.get_by(PortfolioAsset.portfolio_id == portfolio_id, PortfolioAsset.ticker_id == ticker_id)

    async def get_all_by_ticker_and_user_with_portfolios(self, ticker_id: int, user_id: int) -> list[PortfolioAsset]:
        return await self.get_all(PortfolioAsset.ticker_id == ticker_id, PortfolioAsset.user_id == user_id, relations=('portfolio',))

    async def get_all_by_portfolio_tickers(self, portfolio_tickers: dict[int, list[int]]) -> list[PortfolioAsset]:
        conditions = [
            and_(PortfolioAsset.portfolio_id == pid, PortfolioAsset.ticker_id.in_(tickers))
            for pid, tickers in portfolio_tickers.items()
        ]
        return await self.get_all(or_(*conditions)) if conditions else []
