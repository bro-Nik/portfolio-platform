from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, patch

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.core.rate_limit import limiter
from app.di import build_test_container
from app.main import app
from app.modules.auth.repositories import UserRepository
from app.modules.auth.schemas import UserCreate
from app.modules.auth.tasks import send_verification_email


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


@pytest.fixture(autouse=True)
async def clean_tables(test_engine):
    tables = ', '.join(f'"{t.name}"' for t in Base.metadata.sorted_tables)
    async with test_engine.begin() as conn:
        await conn.execute(text(f'TRUNCATE {tables} RESTART IDENTITY CASCADE'))
    yield


@pytest.fixture(autouse=True)
def mock_taskiq():
    with patch.object(send_verification_email, 'kiq', AsyncMock()):
        yield


@pytest.fixture
async def client(db_session):
    original_container = app.state.dishka_container
    app.state.dishka_container = build_test_container(db_session)
    limiter.enabled = False

    try:
        async with (
            LifespanManager(app) as manager,
            AsyncClient(
                transport=ASGITransport(app=manager.app),
                base_url='http://testserver',
                follow_redirects=True,
            ) as client,
        ):
            yield client
    finally:
        app.state.dishka_container = original_container


@pytest.fixture
async def test_user(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    data = UserCreate(
        email='test@example.com',
        password_hash='$2b$12$Yn8dj.X/x2KcyS1twOGkteMqauO4dlECs/zFTzkH5tABpPbMFnFQS',
        role='user',
        status='active',
        is_verified=True,
    )
    return await user_repo.create(data.model_dump())


def _bearer(user_id: int, role: str = 'user') -> dict:
    from datetime import UTC, datetime, timedelta

    import jwt

    from app.common.schemas import UserRole
    from app.core import settings

    payload = {
        'id': str(user_id),
        'role': UserRole(role).value,
        'exp': datetime.now(UTC) + timedelta(hours=1),
        'type': 'access',
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
async def user(db_session: AsyncSession):
    """Пользователь с заполненным профилем (алиас test_user для новых тестов)."""
    repo = UserRepository(db_session)
    return await repo.create(
        UserCreate(
            email='test@example.com',
            password_hash='x',
            role='user',
            status='active',
            is_verified=True,
        ).model_dump()
    )


@pytest.fixture
def auth_headers(user):
    return _bearer(user.id)


@pytest.fixture
def admin_headers(user):
    return _bearer(user.id, 'admin')


@pytest.fixture
def save(db_session):
    async def _save(obj):
        db_session.add(obj)
        await db_session.flush()
        await db_session.refresh(obj)
        return obj

    return _save


@pytest.fixture
async def tickers(db_session, save):
    from app.modules.market.models import Ticker

    return [await save(Ticker(id=i, name=f'Ticker {i}', symbol=f'T{i}', market='crypto')) for i in range(1, 4)]


@pytest.fixture
async def portfolio(db_session, user, save):
    from app.modules.portfolios.models import Portfolio

    return await save(Portfolio(name='Портфель', market='crypto', user_id=user.id))


@pytest.fixture
async def wallet(db_session, user, save):
    from app.modules.portfolios.models import Wallet

    return await save(Wallet(name='Кошелёк', user_id=user.id))


@pytest.fixture
async def refresh_token(db_session, save, user):
    """Refresh-токен пользователя (нужен как FK для login_sessions)."""
    from app.modules.auth.models import RefreshToken

    return await save(
        RefreshToken(
            user_id=user.id,
            token='plain-refresh',
            token_hash='c' * 64,
            expires_at=int((datetime.now(UTC) + timedelta(days=30)).timestamp()),
        )
    )
