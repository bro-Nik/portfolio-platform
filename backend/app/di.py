from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.di import ContextProvider, FastapiProvider, InfraProvider, SessionProvider
from app.modules.auth.dependencies.di import AuthProvider
from app.modules.auth.repositories import UserEmailRepository
from app.modules.market.dependencies.di import MarketProvider, TaskProvider
from app.modules.market.protocols import PriceUpdateObserver, TickerCatalogReader, TickerUsageReader
from app.modules.market.services.ticker import TickerService
from app.modules.portfolios.dependencies.di import PortfoliosProvider
from app.modules.portfolios.repositories import TaggableEntityOwnershipRepository, TickerUsageRepository
from app.modules.tags.dependencies.di import TagsProvider
from app.modules.tags.protocols import EntityOwnershipChecker
from app.modules.watchlist.dependencies.di import WatchlistProvider
from app.modules.watchlist.protocols import UserEmailReader
from app.modules.watchlist.repositories import WatchlistUsageRepository
from app.modules.watchlist.services.alert_evaluator import AlertEvaluatorService


class UnionTickerUsageRepository:
    """Объединяет источники использования тикеров: портфели/кошельки + избранное.

    Живёт в корне композиции, потому что ни portfolios, ни watchlist не могут
    импортировать друг друга напрямую. Без объединения избранное выпадало бы
    из стратегии обновления цен 'used', а удаление/слияние тикеров в админке
    теряло бы записи избранного.
    """

    def __init__(self, portfolios: TickerUsageRepository, watchlist: WatchlistUsageRepository) -> None:
        self._portfolios = portfolios
        self._watchlist = watchlist

    async def get_used_ticker_ids(self, market: str | None = None) -> list[int]:
        portfolio_ids = await self._portfolios.get_used_ticker_ids(market)
        watchlist_ids = await self._watchlist.get_used_ticker_ids(market)
        return sorted(set(portfolio_ids) | set(watchlist_ids))

    async def count_references(self, ticker_id: int) -> int:
        portfolio_refs = await self._portfolios.count_references(ticker_id)
        watchlist_refs = await self._watchlist.count_references(ticker_id)
        return portfolio_refs + watchlist_refs

    async def reassign_references(self, source_id: int, target_id: int) -> None:
        await self._portfolios.reassign_references(source_id, target_id)
        await self._watchlist.reassign_references(source_id, target_id)


class CrossModuleProvider(Provider):
    """Связывает порты модулей с реализациями из других модулей."""

    entity_ownership = provide(
        TaggableEntityOwnershipRepository,
        provides=EntityOwnershipChecker,
        scope=Scope.REQUEST,
    )
    user_emails = provide(
        UserEmailRepository,
        provides=UserEmailReader,
        scope=Scope.REQUEST,
    )
    price_update_observer = provide(
        AlertEvaluatorService,
        provides=PriceUpdateObserver,
        scope=Scope.REQUEST,
    )
    @provide(scope=Scope.REQUEST)
    def get_ticker_catalog(self, ticker_service: TickerService) -> TickerCatalogReader:
        return ticker_service

    @provide(scope=Scope.REQUEST)
    def get_ticker_usage(self, session: AsyncSession) -> TickerUsageReader:
        return UnionTickerUsageRepository(
            TickerUsageRepository(session),
            WatchlistUsageRepository(session),
        )


def build_web_container() -> AsyncContainer:
    """Контейнер web-приложения: сессии, контекст запроса и все модульные провайдеры."""
    return make_async_container(
        FastapiProvider(),
        InfraProvider(),
        SessionProvider(),
        ContextProvider(),
        AuthProvider(),
        TagsProvider(),
        PortfoliosProvider(),
        MarketProvider(),
        WatchlistProvider(),
        CrossModuleProvider(),
    )


def build_worker_container() -> AsyncContainer:
    """Контейнер воркера/планировщика: без FastAPI-зависимостей и контекста запроса."""
    return make_async_container(
        InfraProvider(),
        SessionProvider(),
        MarketProvider(),
        TaskProvider(),
        CrossModuleProvider(),
    )


def _session_override(session: AsyncSession) -> Provider:
    class _TestSessionProvider(Provider):
        @provide(scope=Scope.REQUEST)
        def get_session(self) -> AsyncSession:
            return session

    return _TestSessionProvider()


def build_test_container(session: AsyncSession) -> AsyncContainer:
    """Контейнер для интеграционных тестов: сессия подменяется фикстурой."""
    return make_async_container(
        FastapiProvider(),
        InfraProvider(),
        _session_override(session),
        ContextProvider(),
        AuthProvider(),
        TagsProvider(),
        PortfoliosProvider(),
        MarketProvider(),
        WatchlistProvider(),
        CrossModuleProvider(),
    )
