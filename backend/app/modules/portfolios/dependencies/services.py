from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from app.common.dependencies import Ctx, DBSession
from app.common.redis import get_redis
from app.modules.market.repositories import (
    TickerExternalIdRepository,
    TickerIdentifierRepository,
    TickerRepository,
)
from app.modules.market.services.ticker import TickerService
from app.modules.market.services.ticker_external_id import TickerExternalIdService
from app.modules.market.services.ticker_identifier import TickerIdentifierService
from app.modules.portfolios.services.portfolio import PortfolioService
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.modules.portfolios.services.transaction import TransactionService
from app.modules.portfolios.services.wallet import WalletService
from app.modules.portfolios.services.wallet_asset import WalletAssetService
from app.modules.tags.repositories import TaggableRepository
from app.queries.overview_read import OverviewReadQuery
from app.queries.portfolio_read import PortfolioReadQuery
from app.queries.transaction_read import TransactionReadQuery
from app.queries.wallet_read import WalletReadQuery


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


def get_ticker_service(
    session: DBSession,
    redis: Annotated[Redis, Depends(get_redis)],
) -> TickerService:
    return TickerService(
        session,
        repo=TickerRepository(session),
        ext_id_service=TickerExternalIdService(TickerExternalIdRepository(session)),
        identifier_service=TickerIdentifierService(TickerIdentifierRepository(session)),
        redis=redis,
    )


def get_portfolio_read_query(
    session: DBSession,
    ctx: Ctx,
    ticker_service: Annotated[TickerService, Depends(get_ticker_service)],
) -> PortfolioReadQuery:
    return PortfolioReadQuery(session, ctx, ticker_service=ticker_service)


def get_wallet_read_query(
    session: DBSession,
    ctx: Ctx,
    ticker_service: Annotated[TickerService, Depends(get_ticker_service)],
) -> WalletReadQuery:
    return WalletReadQuery(session, ctx, ticker_service=ticker_service)


def get_transaction_read_query(
    session: DBSession,
    ctx: Ctx,
    ticker_service: Annotated[TickerService, Depends(get_ticker_service)],
) -> TransactionReadQuery:
    return TransactionReadQuery(session, ctx, ticker_service=ticker_service)


def get_overview_read_query(
    session: DBSession,
    ctx: Ctx,
    ticker_service: Annotated[TickerService, Depends(get_ticker_service)],
) -> OverviewReadQuery:
    return OverviewReadQuery(session, ctx, ticker_service=ticker_service)


PortfolioServiceDep = Annotated[PortfolioService, Depends(get_portfolio_service)]
PortfolioAssetServiceDep = Annotated[PortfolioAssetService, Depends(get_portfolio_asset_service)]
WalletServiceDep = Annotated[WalletService, Depends(get_wallet_service)]
WalletAssetServiceDep = Annotated[WalletAssetService, Depends(get_wallet_asset_service)]
TransactionServiceDep = Annotated[TransactionService, Depends(get_transaction_service)]
PortfolioReadQueryDep = Annotated[PortfolioReadQuery, Depends(get_portfolio_read_query)]
WalletReadQueryDep = Annotated[WalletReadQuery, Depends(get_wallet_read_query)]
TransactionReadQueryDep = Annotated[TransactionReadQuery, Depends(get_transaction_read_query)]
OverviewReadQueryDep = Annotated[OverviewReadQuery, Depends(get_overview_read_query)]
