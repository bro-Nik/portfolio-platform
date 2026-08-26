from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.di import ContextProvider, FastapiProvider, InfraProvider, SessionProvider
from app.modules.auth.dependencies.di import AuthProvider
from app.modules.market.dependencies.di import MarketProvider, TaskProvider
from app.modules.market.protocols import TickerUsageReader
from app.modules.portfolios.dependencies.di import PortfoliosProvider
from app.modules.portfolios.repositories import TickerUsageRepository
from app.modules.tags.dependencies.di import TagsProvider


class CrossModuleProvider(Provider):
    """Связывает порты модулей с реализациями из других модулей."""

    ticker_usage = provide(TickerUsageRepository, provides=TickerUsageReader, scope=Scope.REQUEST)


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
        CrossModuleProvider(),
    )
