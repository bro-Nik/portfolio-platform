from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db_session
from app.services.auth import AuthService
from app.services.session import SessionService
from app.services.user import UserService


async def get_auth_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthService:
    """Зависимость для получения сервиса аутентификации."""
    return AuthService(session)


async def get_session_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SessionService:
    """Зависимость для получения сервиса сессий."""
    return SessionService(session)


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserService:
    """Зависимость для получения сервиса пользователей."""
    return UserService(session)
