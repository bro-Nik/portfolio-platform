from contextlib import suppress
from datetime import UTC, datetime, timedelta

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
import jwt
import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.common.schemas import UserRole
from app.core.config import settings
from app.core.database import Base
from app.core.rate_limit import limiter
from app.di import build_test_container
from app.main import app as fastapi_app
import app.modules.auth.models
from app.modules.auth.models import User
from app.modules.market.models import Ticker
import app.modules.portfolios.models
import app.modules.tags.models  # noqa: F401


@pytest.fixture(scope='session')
async def test_engine():
    engine = create_async_engine(
        settings.db_url,
        echo=False,
        connect_args={'command_timeout': 60},
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session(test_engine):
    session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async with session() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture(autouse=True)
async def clean_tables(test_engine):
    tables = ', '.join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    async with test_engine.begin() as conn:
        await conn.execute(text(f'TRUNCATE {tables} RESTART IDENTITY CASCADE'))


@pytest.fixture(autouse=True)
async def clean_redis():
    from app.common.redis import get_redis

    with suppress(RedisConnectionError, OSError):
        await get_redis().flushdb()


@pytest.fixture
async def user(db_session, save):
    return await save(
        db_session,
        User(email='test@example.com', password_hash='test', is_verified=True),
    )


@pytest.fixture
async def client(db_session):
    original_container = fastapi_app.state.dishka_container
    fastapi_app.state.dishka_container = build_test_container(db_session)
    limiter.enabled = False

    try:
        async with (
            LifespanManager(fastapi_app) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url='http://testserver',
                follow_redirects=True,
            ) as client,
        ):
            yield client
    finally:
        fastapi_app.state.dishka_container = original_container


@pytest.fixture
def auth_headers(user):
    payload = {
        'id': str(user.id),
        'role': UserRole.USER,
        'exp': datetime.now(UTC) + timedelta(hours=1),
        'type': 'access',
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def save():
    async def _create(db_session, obj):
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)
        return obj

    return _create


@pytest.fixture
async def tickers(db_session, save):
    return [
        await save(db_session, Ticker(id=i, name=f'Ticker {i}', symbol=f'T{i}', market='crypto')) for i in range(1, 4)
    ]
