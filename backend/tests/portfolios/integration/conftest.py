from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base
from app.core.rate_limit import limiter
from app.common.dependencies import get_session
from app.main import app
from app.modules.portfolios.models import Portfolio, PortfolioAsset, Transaction, Wallet, WalletAsset
from app.common.schemas import UserRole

import app.modules.auth.models  # noqa: F401
import app.modules.portfolios.models  # noqa: F401


@pytest.fixture(scope='session')
async def test_engine():
    engine = create_async_engine(
        settings.db_url,
        echo=False,
        poolclass=NullPool,
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


@pytest.fixture
def user():
    return MagicMock(id=1)


@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_session] = lambda: db_session
    limiter.enabled = False

    async with LifespanManager(app) as manager, AsyncClient(
        transport=ASGITransport(app=manager.app),
        base_url='http://testserver',
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def portfolio(db_session, user, save):
    portfolio = Portfolio(
        name='Тестовый портфель',
        comment='Тестовый комментарий',
        market='crypto',
        user_id=user.id,
    )
    return await save(db_session, portfolio)


@pytest.fixture
async def wallet(db_session, user, save):
    wallet = Wallet(
        name='Тестовый кошелек',
        comment='Тестовый комментарий',
        user_id=user.id,
    )
    return await save(db_session, wallet)


@pytest.fixture
async def portfolio_asset(db_session, portfolio, user, save):
    asset = PortfolioAsset(
        ticker_id='BTC',
        portfolio_id=portfolio.id,
        quantity=Decimal('0.5'),
        buy_orders=Decimal(0),
        sell_orders=Decimal(0),
        amount=Decimal('21500.00'),
        percent=100.0,
        comment='Комментарий',
        user_id=user.id,
    )
    return await save(db_session, asset)


@pytest.fixture
async def wallet_asset(db_session, wallet, user, save):
    asset = WalletAsset(
        ticker_id='BTC',
        wallet_id=wallet.id,
        quantity=Decimal(0),
        buy_orders=Decimal(0),
        sell_orders=Decimal(0),
        user_id=user.id,
    )
    return await save(db_session, asset)


@pytest.fixture
async def transaction(db_session, portfolio, wallet, user, save):
    transaction = Transaction(
        date=datetime.now(UTC),
        ticker_id='BTC',
        ticker2_id='USDT',
        quantity=Decimal('1.5'),
        quantity2=Decimal('20000.0'),
        price=Decimal('15000.00'),
        price_usd=Decimal('14900.00'),
        type='Buy',
        portfolio_id=portfolio.id,
        wallet_id=wallet.id,
        user_id=user.id,
    )
    return await save(db_session, transaction)


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
