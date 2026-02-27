from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING

from fastapi import Depends

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session


@asynccontextmanager
async def session_scope(session_factory: Callable[..., 'AsyncSession']) -> AsyncIterator['AsyncSession']:
    """Асинхронный контекстный менеджер сессии БД."""

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def create_session_dependency(session_factory: Callable) -> Callable:
    """Фабрика зависимости для получения получения сессии БД."""

    async def get_session() -> AsyncIterator['AsyncSession']:
        async with session_scope(session_factory) as session:
            yield session
    
    return Depends(get_session)


@contextmanager
def sync_session(session_factory: Callable[..., 'Session']) -> Iterator['Session']:
    """Синхронный контекстный менеджер для сессии БД."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
