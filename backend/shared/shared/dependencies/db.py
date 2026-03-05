from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import TYPE_CHECKING, Annotated
from dataclasses import dataclass

from fastapi import Depends

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm import Session


@dataclass
class SessionDependencies:
    """Контейнер со всеми зависимостями для работы с БД."""
    
    get_session: Callable[..., AsyncIterator['AsyncSession']]
    DBSession: Annotated['AsyncSession', ...]


def create_dependencies(session_factory: Callable[..., 'AsyncSession']) -> SessionDependencies:
    """Фабрика создает все зависимости для работы с сессиями БД."""
    
    async def get_session() -> AsyncIterator['AsyncSession']:
        """Зависимость для получения асинхронной сессии."""
        async with async_session(session_factory) as session:
            yield session
    
    DBSession = Annotated['AsyncSession', Depends(get_session)]
    
    return SessionDependencies(
        get_session=get_session,
        DBSession=DBSession,
    )


@asynccontextmanager
async def async_session(session_factory: Callable[..., 'AsyncSession']) -> AsyncIterator['AsyncSession']:
    """Асинхронный контекстный менеджер сессии БД."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


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
