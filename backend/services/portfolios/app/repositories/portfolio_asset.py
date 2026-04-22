from sqlalchemy.ext.asyncio import AsyncSession

from shared.repositories import BaseRepository

from app.models import PortfolioAsset


class PortfolioAssetRepository(BaseRepository[PortfolioAsset]):
    """Репозиторий для работы с активами портфелей."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(PortfolioAsset, session)

    async def get_by_ticker_and_portfolio(self, ticker_id: str, portfolio_id: int) -> PortfolioAsset | None:
        """Получить актив портфеля по тикеру."""
        return await self.get_by(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.ticker_id == ticker_id,
        )

    async def get_all_by_ticker_and_user_with_portfolios(self, ticker_id: str, user_id: int) -> list[PortfolioAsset]:
        """Получить активы пользователя по тикеру."""
        return await self.get_all(
            PortfolioAsset.ticker_id == ticker_id,
            PortfolioAsset.user_id == user_id,
            relations=('portfolio',),
        )

    async def get_all_by_tickers_and_portfolio(self, ticker_ids: list[str], portfolio_id: int) -> list[PortfolioAsset]:
        """Получить активы портфеля по списку тикеров."""
        return await self.get_all(
            PortfolioAsset.portfolio_id == portfolio_id,
            PortfolioAsset.ticker_id.in_(ticker_ids),
        )
