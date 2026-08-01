from typing import Annotated

from fastapi import Depends

from app.common.dependencies import Ctx, DBSession

from app.queries.overview_read import OverviewReadQuery
from app.queries.portfolio_read import PortfolioReadQuery
from app.queries.transaction_read import TransactionReadQuery
from app.queries.wallet_read import WalletReadQuery
from app.modules.market.repositories import TickerRepository
from app.modules.portfolios.services.portfolio import PortfolioService
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.modules.portfolios.services.transaction import TransactionService
from app.modules.portfolios.services.wallet import WalletService
from app.modules.portfolios.services.wallet_asset import WalletAssetService
from app.modules.tags.repositories import TaggableRepository


def get_portfolio_service(session: DBSession, ctx: Ctx) -> PortfolioService:
    return PortfolioService(session, ctx, taggable_repo=TaggableRepository(session))


def get_portfolio_asset_service(session: DBSession, ctx: Ctx) -> PortfolioAssetService:
    return PortfolioAssetService(ctx, session)


def get_wallet_service(session: DBSession, ctx: Ctx) -> WalletService:
    return WalletService(session, ctx, taggable_repo=TaggableRepository(session))


def get_wallet_asset_service(session: DBSession, ctx: Ctx) -> WalletAssetService:
    return WalletAssetService(ctx, session)


def get_transaction_service(
    session: DBSession,
    ctx: Ctx,
    portfolio_service: Annotated[PortfolioService, Depends(get_portfolio_service)],
    wallet_service: Annotated[WalletService, Depends(get_wallet_service)],
) -> TransactionService:
    return TransactionService(
        session,
        ctx,
        ticker_repo=TickerRepository(session),
        portfolio_service=portfolio_service,
        wallet_service=wallet_service,
    )


def get_portfolio_read_query(session: DBSession, ctx: Ctx) -> PortfolioReadQuery:
    return PortfolioReadQuery(session, ctx)


def get_wallet_read_query(session: DBSession, ctx: Ctx) -> WalletReadQuery:
    return WalletReadQuery(session, ctx)


def get_transaction_read_query(session: DBSession, ctx: Ctx) -> TransactionReadQuery:
    return TransactionReadQuery(session, ctx)


def get_overview_read_query(session: DBSession, ctx: Ctx) -> OverviewReadQuery:
    return OverviewReadQuery(session, ctx)


PortfolioServiceDep = Annotated[PortfolioService, Depends(get_portfolio_service)]
PortfolioAssetServiceDep = Annotated[PortfolioAssetService, Depends(get_portfolio_asset_service)]
WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service)]
WalletAssetServiceDep = Annotated[WalletAssetService, Depends(get_wallet_asset_service)]
TransactionServiceDep = Annotated[TransactionService, Depends(get_transaction_service)]
PortfolioReadQueryDep = Annotated[PortfolioReadQuery, Depends(get_portfolio_read_query)]
WalletReadQueryDep = Annotated[WalletReadQuery, Depends(get_wallet_read_query)]
TransactionReadQueryDep = Annotated[TransactionReadQuery, Depends(get_transaction_read_query)]
OverviewReadQueryDep = Annotated[OverviewReadQuery, Depends(get_overview_read_query)]
