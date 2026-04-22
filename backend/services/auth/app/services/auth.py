from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import AuthenticationError

from app.core import SecurityService
from app.models import RefreshToken, User
from app.repositories import TokenRepository
from app.schemas import (
    Context,
    RefreshTokenCreate,
    RefreshTokenUpdate,
    TokensResponse,
    UserCreateRequest,
    UserLogin,
    UserRegister,
    UserRole,
)
from app.schemas.token import RefreshTokenRequest
from app.services.session import SessionService
from app.services.user import UserService


@dataclass
class AuthResult:
    tokens: TokensResponse
    user_id: int
    refresh_token_id: int


class AuthService:
    """Сервис аутентификации."""

    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.session = session
        self.token_repo = TokenRepository(session)
        self.user_service = UserService(session, ctx)
        self.session_service = SessionService(session, ctx)
        self.security = SecurityService()

    async def register(self, data: UserRegister) -> AuthResult:
        """Регистрация пользователя."""
        user_data = UserCreateRequest(**data.model_dump(), role=UserRole.USER)  # всегда USER
        user = await self.user_service.create(user_data)
        return await self._create_tokens(user)

    async def login(self, data: UserLogin) -> AuthResult:
        """Аутентификация пользователя."""
        user = await self.user_service.get_for_auth(email=data.email)
        if not self.security.verify_password(data.password, user.password_hash):
            raise AuthenticationError('Неверный email или пароль')

        return await self._create_tokens(user)

    async def refresh_tokens(self, data: RefreshTokenRequest) -> AuthResult:
        """Обновление токенов с валидацией."""
        payload = self.security.verify_token(data.token)
        if payload.get('type') != 'refresh' or not payload.get('id'):
            raise AuthenticationError('Невалидный refresh токен')

        user_id = int(payload['id'])
        user = await self.user_service.get_for_auth(id=user_id)
        token = await self._get_db_refresh_token(data.token)
        return await self._create_tokens(user, token)

    async def logout(self, refresh_token: str) -> bool:
        """Выход из системы."""
        token = await self._get_db_refresh_token(refresh_token)
        return bool(await self.token_repo.delete(token.id))

    async def logout_all(self, user_id: int | None = None) -> bool:
        """Выход из всех устройств."""
        user_id = user_id or self.ctx.actor.id
        return bool(await self.token_repo.delete_all_by_user(user_id))

    async def _get_db_refresh_token(self, refresh_token: str) -> RefreshToken:
        if not (token := await self.token_repo.get_by_token(refresh_token)):
            raise AuthenticationError('Токен не найден в базе')
        return token

    async def _create_tokens(self, user: User, db_token: RefreshToken | None = None) -> AuthResult:
        """Создание пары токенов с сохранением/обновлением refresh в БД."""
        token_data = self.security.create_token_pair(user)
        access = token_data.access_token
        refresh = token_data.refresh_token
        refresh_expires_at = token_data.refresh_expires_at

        if db_token:
            token_to_db = RefreshTokenUpdate(token=refresh, expires_at=refresh_expires_at)
            token = await self.token_repo.update(db_token.id, token_to_db.model_dump())
        else:
            token_to_db = RefreshTokenCreate(user_id=user.id, token=refresh, expires_at=refresh_expires_at)
            token = await self.token_repo.create(token_to_db.model_dump())
            await self.session.flush()

        return AuthResult(
            tokens=TokensResponse(access_token=access, refresh_token=refresh),
            user_id=user.id,
            refresh_token_id=token.id,
        )
