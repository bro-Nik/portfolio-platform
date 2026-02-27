from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

from fastapi import Depends

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def session_scope(session_factory: Callable[..., 'AsyncSession']) -> AsyncIterator['AsyncSession']:
    """Контекстный менеджер для работы с сессией БД."""

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
