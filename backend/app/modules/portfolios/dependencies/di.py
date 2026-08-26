from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.repositories import TickerRepository
from app.modules.market.services.ticker import TickerService
from app.modules.portfolios.services.portfolio import PortfolioService
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.modules.portfolios.services.transaction import TransactionService
from app.modules.portfolios.services.wallet import WalletService
from app.modules.portfolios.services.wallet_asset import WalletAssetService
from app.modules.portfolios.queries import (
    OverviewReadQuery,
    PortfolioReadQuery,
    TransactionReadQuery,
    WalletReadQuery,
)
from app.modules.tags.repositories import TaggableRepository


class PortfoliosProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_portfolio_service(self, session: AsyncSession, ctx: Context) -> PortfolioService:
        return PortfolioService(session, ctx, taggable_repo=TaggableRepository(session))

    @provide(scope=Scope.REQUEST)
    def get_wallet_service(self, session: AsyncSession, ctx: Context) -> WalletService:
        return WalletService(session, ctx, taggable_repo=TaggableRepository(session))

    @provide(scope=Scope.REQUEST)
    def get_portfolio_asset_service(self, session: AsyncSession, ctx: Context) -> PortfolioAssetService:
        return PortfolioAssetService(ctx, session)

    @provide(scope=Scope.REQUEST)
    def get_wallet_asset_service(self, session: AsyncSession, ctx: Context) -> WalletAssetService:
        return WalletAssetService(ctx, session)

    @provide(scope=Scope.REQUEST)
    def get_transaction_service(
        self,
        session: AsyncSession,
        ctx: Context,
        portfolio_service: PortfolioService,
        wallet_service: WalletService,
    ) -> TransactionService:
        return TransactionService(
            session,
            ctx,
            ticker_repo=TickerRepository(session),
            portfolio_service=portfolio_service,
            wallet_service=wallet_service,
        )

    @provide(scope=Scope.REQUEST)
    def get_portfolio_read_query(
        self,
        session: AsyncSession,
        ctx: Context,
        ticker_service: TickerService,
    ) -> PortfolioReadQuery:
        return PortfolioReadQuery(session, ctx, ticker_service=ticker_service)

    @provide(scope=Scope.REQUEST)
    def get_wallet_read_query(
        self,
        session: AsyncSession,
        ctx: Context,
        ticker_service: TickerService,
    ) -> WalletReadQuery:
        return WalletReadQuery(session, ctx, ticker_service=ticker_service)

    @provide(scope=Scope.REQUEST)
    def get_transaction_read_query(
        self,
        session: AsyncSession,
        ctx: Context,
        ticker_service: TickerService,
    ) -> TransactionReadQuery:
        return TransactionReadQuery(session, ctx, ticker_service=ticker_service)

    @provide(scope=Scope.REQUEST)
    def get_overview_read_query(
        self,
        session: AsyncSession,
        ctx: Context,
        ticker_service: TickerService,
    ) -> OverviewReadQuery:
        return OverviewReadQuery(session, ctx, ticker_service=ticker_service)
