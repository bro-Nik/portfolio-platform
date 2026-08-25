from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.auth.services.auth import AuthService
from app.modules.auth.services.session import SessionService
from app.modules.auth.services.user import UserService


class AuthProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_service(self, session: AsyncSession, ctx: Context) -> UserService:
        return UserService(session, ctx)

    @provide(scope=Scope.REQUEST)
    def get_session_service(self, session: AsyncSession, ctx: Context) -> SessionService:
        return SessionService(session, ctx)

    @provide(scope=Scope.REQUEST)
    def get_auth_service(self, session: AsyncSession, ctx: Context) -> AuthService:
        return AuthService(session, ctx)
