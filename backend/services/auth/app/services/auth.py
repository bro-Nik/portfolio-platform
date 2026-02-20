from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import SecurityService
from app.repositories import TokenRepository
from app.schemas import (
    RefreshTokenCreate,
    RefreshTokenUpdate,
    UserCreateRequest,
    UserLogin,
    UserRole,
    UserSchema,
    TokensResponse
)
from app.services.user import UserService


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

    async def register(self, user_data: UserLogin) -> tuple[TokensResponse, int, int]:
        """Регистрация пользователя (роль USER)."""
        user_data = UserCreateRequest(**user_data.model_dump())
        user_data.role = UserRole.USER

        user = await self.user_service.create_user(user_data)
        return await self._create_tokens(user)

    async def login(self, user_data: UserLogin) -> tuple[TokensResponse, int, int]:
        """Аутентификация пользователя."""
        user = await self.user_service.get_user_by_email(user_data.email)
        if user and self.security.verify_password(user_data.password, user.password_hash):
            return await self._create_tokens(user)

        raise AuthenticationError('Неверный email или пароль')

    async def refresh_tokens(self, refresh_token: str) -> tuple[TokensResponse, int, int]:
        """Обновление токенов с валидацией."""
        # Валидация токена
        payload = self.security.verify_token(refresh_token)
        if payload.get('type') != 'refresh' or not payload.get('sub'):
            raise AuthenticationError('Невалидный refresh токен')

        # Проверка в БД
        stored_token = await self.token_repo.get_by_token(refresh_token)
        if not stored_token:
            raise AuthenticationError('Токен не найден в базе')

        # Проверка срока действия
        if self.security.is_token_expired(stored_token.expires_at):
            await self.token_repo.delete(stored_token.id)
            raise AuthenticationError('Токен истек')

        # Генерация новых токенов
        user_id = int(payload['sub'])
        user = await self.user_service.get_user_by_id(user_id)
        access_token, refresh_token, refresh_expires_at = self._generate_tokens(user)

        # Обновление токена в БД
        token_update = RefreshTokenUpdate(
            token=refresh_token,
            expires_at=refresh_expires_at,
        )

        await self.token_repo.update(stored_token.id, token_update)

        tokens = TokensResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        return tokens, user_id, stored_token.id

    async def logout(self, refresh_token: str) -> bool:
        """Выход из системы."""
        token = await self.token_repo.get_by_token(refresh_token)
        if token:
            return await self.token_repo.delete(token.id)
        return False

    async def logout_all(self, user_id: int) -> bool:
        """Выход из всех устройств."""
        return bool(await self.token_repo.delete_user_tokens(user_id))

    async def _create_tokens(self, user: UserSchema) -> tuple[TokensResponse, int, int]:
        """Создание пары токенов с сохранением refresh в БД."""
        access_token, refresh_token, refresh_expires_at = self._generate_tokens(user)

        # Сохраняем refresh токен в базу
        token_data = RefreshTokenCreate(
            user_id=user.id,
            token=refresh_token,
            expires_at=refresh_expires_at,
        )

        db_token = await self.token_repo.create(token_data)
        await self.session.flush()

        tokens = TokensResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        return tokens, user.id, db_token.id

    def _generate_tokens(self, user: UserSchema) -> tuple[str, str, int]:
        """Генерация токенов."""
        if not user:
            raise AuthenticationError('Пользователь не найден')

        access_token = self.security.create_access_token(user)
        refresh_token = self.security.create_refresh_token(user)

        # Валидация сгенерированного refresh токена
        refresh_payload = self.security.verify_token(refresh_token)

        refresh_expires_at = refresh_payload['exp']
        return access_token, refresh_token, refresh_expires_at
