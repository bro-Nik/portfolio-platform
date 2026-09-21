from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core import settings


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(
    settings.db_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    # Без явного таймаута задача ждёт свободное соединение 30 с (дефолт
    # SQLAlchemy) и падает TimeoutError, который никто не видит.
    pool_timeout=settings.db_pool_timeout,
    # Сторожевой таймаут на стороне PostgreSQL: патологический запрос не должен
    # держать соединение пула бесконечно.
    connect_args={'server_settings': {'statement_timeout': str(settings.db_statement_timeout_ms)}},
    echo=settings.db_echo,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
