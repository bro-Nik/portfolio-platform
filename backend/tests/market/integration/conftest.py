from contextlib import suppress
from datetime import UTC, datetime
from decimal import Decimal

import pytest
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import settings
from app.core.database import Base
from app.modules import models as _models  # noqa: F401  # регистрация ORM-моделей
from app.modules.market.models import Ticker
from app.modules.market.protocols import TickerUsageReader
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
    async def get_used_ticker_ids(self) -> list[int]:
        return []

    async def count_references(self, ticker_id: int) -> int:
        return 0

    async def reassign_references(self, source_id: int, target_id: int) -> None:
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
        redis=None,
    )


@pytest.fixture
def tickers(db_session):
    def _make(*specs: tuple[str, str]) -> list[Ticker]:
        rows = [
            Ticker(name=name, symbol=symbol, market=market, price=0.0, updated_at=datetime.now(UTC))
            for name, symbol, market in specs
        ]
        db_session.add_all(rows)
        return rows

    return _make


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


@pytest.fixture
def decimal_zero():
    return Decimal(0)
