from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Annotated

from dishka import FromDishka, Provider, Scope, make_async_container, provide
import redis.asyncio as redis
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import settings
from app.core.database import AsyncSessionLocal
from app.modules.market.external_api.core import (
    BaseProvider,
    HTTPClient,
    LimiterConfig,
    RateLimiter,
    RequestLogger,
    registry,
)
from app.modules.market.repositories import ProviderRepository, RequestLogRepository, TaskRepository
from app.modules.market.services.provider import ProviderService
from app.modules.market.services.task import TaskService
from app.modules.market.services.task_tracker import TaskTrackerService
from app.modules.market.services.ticker import TickerService

SessionFactory = async_sessionmaker[AsyncSession]


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis(self) -> Redis:
        return await redis.from_url(settings.redis_url)

    @provide(scope=Scope.APP)
    async def get_session_factory(self) -> SessionFactory:
        return AsyncSessionLocal

    @provide(scope=Scope.REQUEST)
    async def get_session(self, session_factory: SessionFactory) -> AsyncIterator[AsyncSession]:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    @provide(scope=Scope.REQUEST)
    def get_task_repo(self, session: AsyncSession) -> TaskRepository:
        return TaskRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_provider_repo(self, session: AsyncSession) -> ProviderRepository:
        return ProviderRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_request_log_repo(self, session: AsyncSession) -> RequestLogRepository:
        return RequestLogRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_task_service(self, session: AsyncSession, task_repo: TaskRepository, provider_repo: ProviderRepository) -> TaskService:
        return TaskService(session=session, task_repo=task_repo, provider_repo=provider_repo)

    @provide(scope=Scope.REQUEST)
    def get_ticker_service(self, session: AsyncSession) -> TickerService:
        return TickerService(session)

    @provide(scope=Scope.REQUEST)
    def get_provider_service(self, session: AsyncSession, redis: Redis, provider_repo: ProviderRepository, log_repo: RequestLogRepository) -> ProviderService:
        return ProviderService(session=session, redis=redis, provider_repo=provider_repo, log_repo=log_repo)


class TaskProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_task_tracker_service(self, session_factory: SessionFactory) -> TaskTrackerService:
        return TaskTrackerService(session_factory)

    @provide(scope=Scope.REQUEST)
    def get_provider_factory(self, redis: Redis, session_factory: SessionFactory, provider_service: ProviderService) -> Callable[[str, int], Awaitable[BaseProvider]]:
        async def factory(provider_name: str, task_id: int) -> BaseProvider:
            provider_class = registry.get_provider(provider_name)
            config = await provider_service.get_config_by_name(provider_name)
            limiter_config = LimiterConfig(
                key=provider_name,
                requests_per_minute=config.requests_per_minute,
                requests_per_hour=config.requests_per_hour,
                requests_per_day=config.requests_per_day,
                requests_per_month=config.requests_per_month,
            )
            limiter = RateLimiter(redis=redis, config=limiter_config)
            logger = RequestLogger(provider_name, task_id, session_factory=session_factory)
            http = HTTPClient(provider_class.BASE_URL, limiter=limiter, logger=logger)
            return provider_class(http, api_key=config.api_key)
        return factory


container = make_async_container(AppProvider())

ProviderServiceDep = Annotated[FromDishka[ProviderService], ...]
TaskServiceDep = Annotated[FromDishka[TaskService], ...]
TickerServiceDep = Annotated[FromDishka[TickerService], ...]
SessionDep = Annotated[FromDishka[AsyncSession], ...]

TaskTrackerServiceDep = Annotated[FromDishka[TaskTrackerService], ...]
ProviderFactoryDep = Annotated[FromDishka[Callable[[str, int], Awaitable[BaseProvider]]], ...]
