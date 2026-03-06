from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core import settings
from app.dependencies import get_session
from app.main import app
from app.models import Base
from app.repositories import UserRepository
from app.schemas import UserCreate


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


@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_session] = lambda: db_session

    async with LifespanManager(app) as manager, AsyncClient(
        transport=ASGITransport(app=manager.app),
        base_url='http://testserver',
    ) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession):
    user_repo = UserRepository(db_session)

    user = await user_repo.get_by_email('test@example.com')
    if user:
        return user

    data = UserCreate(
        email='test@example.com',
        password_hash='$2b$12$Yn8dj.X/x2KcyS1twOGkteMqauO4dlECs/zFTzkH5tABpPbMFnFQS',  # "testpass"
        role='user',
        status='active',
    )
    user = await user_repo.create(data)
    await db_session.commit()
    return user
