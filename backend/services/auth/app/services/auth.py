from dataclasses import dataclass

from shared.exceptions import AuthenticationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import SecurityService
from app.models import RefreshToken
from app.repositories import TokenRepository
from app.schemas import (
    AuthUser,
    RefreshTokenCreate,
    RefreshTokenUpdate,
    TokensResponse,
    UserCreateRequest,
    UserLogin,
    UserRegister,
    UserRole,
)
from app.schemas.token import RefreshTokenRequest
from app.services.user import UserService


@dataclass
class AuthResult:
    tokens: TokensResponse
    user_id: int
    refresh_token_id: int


class AuthService:
    """Сервис аутентификации."""

    def __init__(
        self,
        session: AsyncSession,
        token_repo: TokenRepository | None = None,
        user_service: UserService | None = None,
        security: SecurityService | None = None,
    ) -> None:
        self.session = session
        self.token_repo = token_repo or TokenRepository(session)
        self.user_service = user_service or UserService(session)
        self.security = security or SecurityService()

    async def register(self, data: UserRegister) -> AuthResult:
        """Регистрация пользователя."""
        user_data = UserCreateRequest(**data.model_dump(), role=UserRole.USER)  # всегда USER
        user = await self.user_service.create(user_data)
        return await self._create_tokens(user)

    async def login(self, data: UserLogin) -> AuthResult:
        """Аутентификация пользователя."""
        user = await self.user_service.get_by_email(data.email)
        if not self.security.verify_password(data.password, user.password_hash):
            raise AuthenticationError('Неверный email или пароль')

        return await self._create_tokens(user)

    async def refresh_tokens(self, data: RefreshTokenRequest) -> AuthResult:
        """Обновление токенов с валидацией."""
        payload = self.security.verify_token(data.token)
        if payload.get('type') != 'refresh' or not payload.get('id'):
            raise AuthenticationError('Невалидный refresh токен')

        user_id = int(payload['id'])
        user = await self.user_service.get(user_id)
        token = await self._get_refresh_token(data.token)
        return await self._create_tokens(user, token)

    async def logout(self, refresh_token: str) -> bool:
        """Выход из системы."""
        token = await self._get_refresh_token(refresh_token)
        return await self.token_repo.delete(token.id)

    async def logout_all(self, user_id: int) -> bool:
        """Выход из всех устройств."""
        return bool(await self.token_repo.delete_many_by_user(user_id))

    async def _get_refresh_token(self, refresh_token: str) -> RefreshToken:
        if not (token := await self.token_repo.get_by_token(refresh_token)):
            raise AuthenticationError('Токен не найден в базе')
        return token

    async def _create_tokens(self, user: AuthUser, db_token: RefreshToken | None = None) -> AuthResult:
        """Создание пары токенов с сохранением/обновлением refresh в БД."""
        token_data = self.security.create_token_pair(user)
        access = token_data.access_token
        refresh = token_data.refresh_token
        refresh_expires_at = token_data.refresh_expires_at

        if db_token:
            token_to_db = RefreshTokenUpdate(token=refresh, expires_at=refresh_expires_at)
            token = await self.token_repo.update(db_token.id, token_to_db)
        else:
            token_to_db = RefreshTokenCreate(user_id=user.id, token=refresh, expires_at=refresh_expires_at)
            token = await self.token_repo.create(token_to_db)
            await self.session.flush()

        return AuthResult(
            tokens=TokensResponse(access_token=access, refresh_token=refresh),
            user_id=user.id,
            refresh_token_id=token.id,
        )
