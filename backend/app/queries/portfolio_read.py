from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.repositories.ticker import TickerRepository
from app.modules.portfolios.models import Portfolio, PortfolioAsset
from app.modules.portfolios.repositories import TransactionRepository
from app.modules.tags.repositories import TaggableRepository
from app.modules.portfolios.services.portfolio import PortfolioService

IMAGES_URL = '/market/static/images/tickers'


class PortfolioReadQuery:
    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.session = session
        self.ctx = ctx
        self.taggable_repo = TaggableRepository(session)
        self.service = PortfolioService(session, ctx, taggable_repo=self.taggable_repo)
        self.ticker_repo = TickerRepository(session)
        self.transaction_repo = TransactionRepository(session)

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

    async def _add_has_transactions(self, portfolios: list[Portfolio]) -> None:
        portfolio_ids = [p.id for p in portfolios]
        portfolio_txn_ids = await self.transaction_repo.portfolios_with_transactions(portfolio_ids)
        for p in portfolios:
            p.has_transactions = p.id in portfolio_txn_ids

        all_assets = [a for p in portfolios for a in p.assets]
        portfolio_per_asset = {a.id: p.id for p in portfolios for a in p.assets}
        assets_by_portfolio: dict[int, list] = {}
        for a in all_assets:
            pid = portfolio_per_asset[a.id]
            assets_by_portfolio.setdefault(pid, []).append(a)
        portfolio_tickers = {
            pid: [a.ticker_id for a in assets]
            for pid, assets in assets_by_portfolio.items()
        }
        txn_pairs = await self.transaction_repo.portfolios_tickers_with_transactions(
            portfolio_tickers,
        )
        for a in all_assets:
            a.has_transactions = (portfolio_per_asset[a.id], a.ticker_id) in txn_pairs

    async def enrich_single_asset(self, asset: PortfolioAsset) -> PortfolioAsset:
        tickers_list = await self.ticker_repo.get_all_by_ids([asset.ticker_id])
        if tickers_list:
            t = tickers_list[0]
            asset.name = t.name
            asset.symbol = t.symbol
            asset.image = f'{IMAGES_URL}/{t.market}/24/{t.image}' if t.image else None
        asset.tags = await self.taggable_repo.get_tags(self.service.ASSET_ENTITY_TYPE, asset.id)
        asset.has_transactions = False
        return asset

    async def get_with_assets(self, id: int) -> Portfolio:
        portfolio = await self.service.get_with_assets(id)
        await self._enrich([portfolio])
        await self._add_has_transactions([portfolio])
        return portfolio

    async def get_all_with_assets(self) -> list[Portfolio]:
        portfolios = await self.service.get_all_with_assets()
        await self._enrich(portfolios)
        await self._add_has_transactions(portfolios)
        return portfolios
