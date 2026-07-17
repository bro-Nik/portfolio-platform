from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import Base
from app.core.rate_limit import limiter
from app.common.dependencies import get_session
from app.main import app

from app.modules.auth.repositories import UserRepository
from app.modules.auth.schemas import UserCreate
from app.modules.auth.tasks import send_verification_email

import app.modules.auth.models  # noqa: F401


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


@pytest.fixture(autouse=True)
def mock_taskiq():
    with patch.object(send_verification_email, 'kiq', AsyncMock()):
        yield


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
