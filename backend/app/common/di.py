from collections.abc import AsyncIterator
import uuid

from dishka import Provider, Scope, provide
from dishka.integrations.fastapi import FastapiProvider
from fastapi import Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.common.dependencies.auth import get_actor_from_headers
from app.common.redis import get_redis as get_common_redis
from app.common.schemas import Context
from app.common.utils import get_client_ip
from app.core.database import AsyncSessionLocal

SessionFactory = async_sessionmaker[AsyncSession]


class InfraProvider(Provider):
    @provide(scope=Scope.APP)
    def get_redis(self) -> Redis:
        return get_common_redis()

    @provide(scope=Scope.APP)
    async def get_session_factory(self) -> SessionFactory:
        return AsyncSessionLocal


class SessionProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(self, session_factory: SessionFactory) -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise


class ContextProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_context(self, request: Request) -> Context:
        return Context(
            _actor=get_actor_from_headers(request.headers.get('authorization')),
            client_ip=get_client_ip(request),
            request_id=request.headers.get('X-Request-ID', str(uuid.uuid4())),
            user_agent=request.headers.get('user-agent'),
        )


__all__ = [
    'ContextProvider',
    'FastapiProvider',
    'InfraProvider',
    'SessionFactory',
    'SessionProvider',
]
