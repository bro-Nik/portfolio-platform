from typing import Annotated

from fastapi import Depends

from app.dependencies import Ctx, DBSession
from app.services import AuthService, SessionService, UserService


async def get_auth_service(session: DBSession, ctx: Ctx) -> AuthService:
    """Зависимость для получения сервиса аутентификации."""
    return AuthService(session, ctx)


async def get_session_service(session: DBSession, ctx: Ctx) -> SessionService:
    """Зависимость для получения сервиса сессий."""
    return SessionService(session, ctx)


async def get_user_service(session: DBSession, ctx: Ctx) -> UserService:
    """Зависимость для получения сервиса пользователей."""
    return UserService(session, ctx)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
