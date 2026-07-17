from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.repositories.ticker import TickerRepository
from app.modules.portfolios.models import Portfolio
from app.modules.portfolios.services.portfolio import PortfolioService

IMAGES_URL = '/market/static/images/tickers'


class PortfolioReadQuery:
    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.session = session
        self.ctx = ctx
        self.service = PortfolioService(session, ctx)
        self.ticker_repo = TickerRepository(session)

    async def _enrich(self, portfolios: list[Portfolio]) -> None:
        all_assets = [a for p in portfolios for a in p.assets]
        if not all_assets:
            return
        ticker_ids = list(set(a.ticker_id for a in all_assets))
        tickers_list = await self.ticker_repo.get_all_by_ids(ticker_ids)
        ticker_map = {t.id: t for t in tickers_list}
        for asset in all_assets:
            t = ticker_map.get(asset.ticker_id)
            if t:
                asset.name = t.name
                asset.symbol = t.symbol
                asset.image = f'{IMAGES_URL}/{t.market}/24/{t.image}' if t.image else None

    async def get_with_assets(self, id: int) -> Portfolio:
        portfolio = await self.service.get_with_assets(id)
        await self._enrich([portfolio])
        return portfolio

    async def get_all_with_assets(self) -> list[Portfolio]:
        portfolios = await self.service.get_all_with_assets()
        await self._enrich(portfolios)
        return portfolios
