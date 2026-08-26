from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.services.ticker import TickerService
from app.modules.portfolios.models import Portfolio, Wallet
from app.modules.portfolios.queries.enrichment import enrich_assets_with_ticker_info
from app.modules.portfolios.queries.portfolio_read import PortfolioReadQuery
from app.modules.portfolios.queries.wallet_read import WalletReadQuery


class OverviewReadQuery:
    def __init__(self, session: AsyncSession, ctx: Context, ticker_service: TickerService) -> None:
        self.session = session
        self.ctx = ctx
        self.ticker_service = ticker_service
        self.portfolio_query = PortfolioReadQuery(session, ctx, ticker_service)
        self.wallet_query = WalletReadQuery(session, ctx, ticker_service)

    async def get_all(self) -> tuple[list[Portfolio], list[Wallet]]:
        portfolios = await self.portfolio_query.service.get_all_with_assets()
        wallets = await self.wallet_query.service.get_all_with_assets()

        all_assets = [a for p in portfolios for a in p.assets] + [a for w in wallets for a in w.assets]
        await enrich_assets_with_ticker_info(all_assets, self.ticker_service)
        await self.portfolio_query.add_has_transactions(portfolios)
        await self.wallet_query.add_has_transactions(wallets)

        return portfolios, wallets
