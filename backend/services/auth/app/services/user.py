from shared.exceptions import BusinessRuleError, ConflictError, NotFoundError, PermissionDeniedError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import SecurityService
from app.models import User
from app.repositories import UserRepository
from app.schemas import (
    AuthUser,
    UserCreate,
    UserCreateRequest,
    UserRole,
    UserUpdate,
    UserUpdateRequest,
)


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(
        self,
        session: AsyncSession,
        user_repo: UserRepository | None = None,
        security_service: SecurityService | None = None,
    ) -> None:
        self.session = session
        self.repo = user_repo or UserRepository(session)
        self.security = security_service or SecurityService()

    async def get(self, user_id: int) -> User:
        """Получить пользователя по ID."""
        if not (user := await self.repo.get(user_id)):
            raise NotFoundError(f'Пользователь id={user_id} не найден')
        return user

    async def get_by_email(self, email: str) -> User:
        """Получить пользователя по email."""
        if not (user := await self.repo.get_by_email(email)):
            raise NotFoundError(f'Пользователь email={email} не найден')
        return user

    async def get_detailed(self, user_id: int) -> User:
        """Получить пользователя по ID с детальной информацией."""
        if not (user := await self.repo.get_with_sessions(user_id)):
            raise NotFoundError(f'Пользователь id={user_id} не найден')
        return user

    async def get_many_detailed(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        role: str | None = None,
    ) -> list[User]:
        """Получить список пользователей с детальной информацией."""
        return await self.repo.get_many_with_sessions(skip, limit, search, role)

    async def create(self, data: UserCreateRequest, actor: AuthUser | None = None) -> User:
        """Создать нового пользователя."""
        # actor может быть None для регистрации
        await self._validate_create_data(data, actor)

        user_to_db = UserCreate(
            **data.model_dump(exclude={'password'}),
            password_hash=self.security.get_password_hash(data.password),
        )

        user = await self.repo.create(user_to_db)
        await self.session.flush()
        return user

    async def update(self, user_id: int, data: UserUpdateRequest, actor: AuthUser) -> User:
        """Обновить пользователя."""
        user = await self.get(user_id)
        await self._check_permission(actor, user)
        await self._validate_update_data(data, actor, user)

        user_to_db = UserUpdate(**data.model_dump())
        return await self.repo.update(user_id, user_to_db)

    async def delete(self, user_id: int, actor: AuthUser) -> None:
        """Удалить пользователя."""
        user = await self.get(user_id)
        await self._check_permission(actor, user)
        await self.repo.delete(user_id)

    async def update_activity(self, user_id:int) -> None:
        """Обновить метрики активности пользователя."""
        await self.repo.update_activity(user_id)

    async def _check_permission(self, actor: AuthUser, target_user: User) -> None:
        if actor.id == target_user.id:
            return
        if actor.role.priority > target_user.role.priority:
            return

        raise PermissionDeniedError('Недостаточно прав для изменения пользователя')

    async def _validate_create_data(self, data: UserCreateRequest, actor: AuthUser) -> None:
        if actor and data.role.priority >= actor.role.priority:
            raise BusinessRuleError('Нельзя назначать права, равные или превышающие ваши')

        if not actor and data.role != UserRole.USER:
            raise BusinessRuleError('Неверные права для пользователя: превышает USER')

        if await self.repo.exists_by(User.email == data.email):
            raise ConflictError(f'Пользователь с email {data.email} уже существует')

    async def _validate_update_data(self, data: UserUpdateRequest, actor: AuthUser, user: User) -> None:
        if user.id == actor.id and data.role.priority <= actor.role.priority:
            return

        if data.role.priority >= actor.role.priority:
            raise BusinessRuleError('Нельзя назначать права, равные или превышающие ваши')
