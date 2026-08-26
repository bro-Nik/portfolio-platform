from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.services.ticker import TickerService
from app.modules.portfolios.models import Portfolio, PortfolioAsset
from app.modules.portfolios.queries.enrichment import add_has_transactions, enrich_assets_with_ticker_info
from app.modules.portfolios.repositories import TransactionRepository
from app.modules.portfolios.services.portfolio import PortfolioService
from app.modules.tags.repositories import TaggableRepository


class PortfolioReadQuery:
    def __init__(self, session: AsyncSession, ctx: Context, ticker_service: TickerService) -> None:
        self.session = session
        self.ctx = ctx
        self.ticker_service = ticker_service
        self.taggable_repo = TaggableRepository(session)
        self.service = PortfolioService(session, ctx, taggable_repo=self.taggable_repo)
        self.transaction_repo = TransactionRepository(session)

    async def enrich(self, portfolios: list[Portfolio]) -> None:
        await enrich_assets_with_ticker_info(
            [a for p in portfolios for a in p.assets],
            self.ticker_service,
        )

    async def add_has_transactions(self, portfolios: list[Portfolio]) -> None:
        await add_has_transactions(
            portfolios,
            [a for p in portfolios for a in p.assets],
            parents_with_transactions=self.transaction_repo.portfolios_with_transactions,
            parent_tickers_with_transactions=self.transaction_repo.portfolios_tickers_with_transactions,
        )

    async def enrich_single_asset(self, asset: PortfolioAsset) -> PortfolioAsset:
        info = (await self.ticker_service.get_info([asset.ticker_id])).get(asset.ticker_id)
        if info:
            asset.name = info.name
            asset.symbol = info.symbol
            asset.image = info.image
            asset.market = info.market
        asset.tags = await self.taggable_repo.get_tags(self.service.ASSET_ENTITY_TYPE, asset.id)
        asset.has_transactions = False
        return asset

    async def get_with_assets(self, id: int) -> Portfolio:
        portfolio = await self.service.get_with_assets(id)
        await self.enrich([portfolio])
        await self.add_has_transactions([portfolio])
        return portfolio

    async def get_all_with_assets(self) -> list[Portfolio]:
        portfolios = await self.service.get_all_with_assets()
        await self.enrich(portfolios)
        await self.add_has_transactions(portfolios)
        return portfolios
