from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.market.services.ticker import TickerService
from app.modules.watchlist.services.alert import AlertService
from app.modules.watchlist.services.watchlist import WatchlistService


class WatchlistProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_watchlist_service(
        self,
        session: AsyncSession,
        ctx: Context,
        ticker_service: TickerService,
    ) -> WatchlistService:
        return WatchlistService(session, ctx, ticker_service=ticker_service)

    @provide(scope=Scope.REQUEST)
    def get_alert_service(
        self,
        session: AsyncSession,
        ctx: Context,
        ticker_service: TickerService,
    ) -> AlertService:
        return AlertService(session, ctx, ticker_service=ticker_service)
