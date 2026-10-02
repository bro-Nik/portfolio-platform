from contextlib import suppress
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.common.schemas import UserRole
from app.core import settings
from app.core.database import Base
from app.modules import models as _models  # noqa: F401  # регистрация ORM-моделей
from app.modules.market.models import Ticker
from app.modules.market.protocols import PriceUpdateObserver, TickerUsageReader
from app.modules.market.repositories import (
    TickerExternalIdRepository,
    TickerIdentifierRepository,
    TickerRepository,
)
from app.modules.market.services.ticker import TickerService
from app.modules.market.services.ticker_external_id import TickerExternalIdService
from app.modules.market.services.ticker_identifier import TickerIdentifierService


@pytest.fixture(scope='session')
async def test_engine():
    engine = create_async_engine(settings.db_url, echo=False, connect_args={'command_timeout': 60})

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


class _NoUsage(TickerUsageReader):
    async def get_used_ticker_ids(self, market: str | None = None) -> list[int]:
        return []

    async def count_references(self, ticker_id: int) -> int:
        return 0

    async def reassign_references(self, source_id: int, target_id: int) -> None:
        return None


class _NoAlerts(PriceUpdateObserver):
    async def on_prices_updated(self, prices: dict[int, float]) -> None:
        return None


@pytest.fixture
def ticker_service(db_session):
    repo = TickerRepository(db_session)
    return TickerService(
        db_session,
        repo,
        TickerExternalIdService(TickerExternalIdRepository(db_session)),
        TickerIdentifierService(TickerIdentifierRepository(db_session)),
        _NoUsage(),
        _NoAlerts(),
        redis=None,
    )


@pytest.fixture
def extract_identifiers():
    """Извлекает адреса контрактов из ответа CoinGecko-подобного провайдера."""

    def _extract(coin: dict) -> dict[str, str]:
        return {f'contract_{chain}': addr for chain, addr in (coin.get('platforms') or {}).items()}

    return _extract


@pytest.fixture
async def save(db_session):
    async def _save(obj):
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)
        return obj

    return _save


def _bearer(role: str) -> dict:
    payload = {
        'id': '1',
        'role': role,
        'exp': datetime.now(UTC) + timedelta(hours=1),
        'type': 'access',
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def auth_headers():
    """Токен обычного пользователя."""
    return _bearer(UserRole.USER.value)


@pytest.fixture
def admin_headers():
    """Токен администратора для /market/admin и /auth/admin роутов."""
    return _bearer(UserRole.ADMIN.value)


@pytest.fixture
async def market_client(db_session):
    """HTTP-клиент для market-роутов (они живут вне общего /api префикса)."""
    from asgi_lifespan import LifespanManager
    from httpx import ASGITransport, AsyncClient

    from app.core.rate_limit import limiter
    from app.di import build_test_container
    from app.main import app as fastapi_app

    original = fastapi_app.state.dishka_container
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
        fastapi_app.state.dishka_container = original


@pytest.fixture
async def user(db_session, save):
    """Пользователь для тестов, где нужен реальный FK."""
    from app.modules.auth.models import User

    return await save(User(email='user@example.com', password_hash='x', is_verified=True))


@pytest.fixture
async def tickers(db_session, save):
    """Тикеры для тестов, которым нужен реальный FK на ticker."""
    return [await save(Ticker(name=f'Ticker {i}', symbol=f'T{i}', market='crypto', price=0.0)) for i in range(1, 4)]
