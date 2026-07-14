from typing import Annotated

from fastapi import Depends

from app.modules.auth.services.auth import AuthService
from app.modules.auth.services.session import SessionService
from app.modules.auth.services.user import UserService

from app.common.dependencies import Ctx, DBSession


async def get_auth_service(session: DBSession, ctx: Ctx) -> AuthService:
    return AuthService(session, ctx)


async def get_user_service(session: DBSession, ctx: Ctx) -> UserService:
    return UserService(session, ctx)


async def get_session_service(session: DBSession, ctx: Ctx) -> SessionService:
    return SessionService(session, ctx)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
SessionServiceDep = Annotated[SessionService, Depends(get_session_service)]
