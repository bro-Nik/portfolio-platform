from datetime import UTC, datetime, timedelta
from decimal import Decimal

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
import jwt
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from app.core.config import settings
from app.core.database import Base
from app.core.rate_limit import limiter
from app.common.dependencies import get_session

import app.modules.auth.models  # noqa: F401
import app.modules.portfolios.models  # noqa: F401
import app.modules.tags.models  # noqa: F401

from app.main import app
from app.modules.auth.models import User
from app.modules.portfolios.models import Portfolio, PortfolioAsset, Transaction, Wallet, WalletAsset
from app.common.schemas import UserRole


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
    yield


@pytest.fixture
async def user(db_session, save):
    return await save(
        db_session,
        User(email='test@example.com', password_hash='test', is_verified=True),
    )


@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_session] = lambda: db_session
    limiter.enabled = False

    async with LifespanManager(app) as manager, AsyncClient(
        transport=ASGITransport(app=manager.app),
        base_url='http://testserver',
        follow_redirects=True,
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
        ticker_id=1,
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
        ticker_id=1,
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
        ticker_id=1,
        ticker2_id=2,
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
