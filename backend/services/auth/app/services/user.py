from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from app.core.security import SecurityService
from app.models import User
from app.repositories import UserRepository
from app.schemas import (
    UserSchema,
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

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID."""
        return await self.repo.get(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        return await self.repo.get_by_email(email)

    async def get_user_with_details(self, user_id: int) -> User | None:
        """Получить пользователя по ID с детальной информацией."""
        user = await self.repo.get(user_id, relations=('login_sessions',))
        if not user:
            raise NotFoundError('Пользователь не найден')
        return user

    async def get_users_with_details(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        role: str | None = None,
    ) -> list[User]:
        """Получить спис пользователей."""
        return await self.repo.get_many_with_sessions(skip, limit, search, role)

    async def create_user(
        self,
        user_data: UserCreateRequest,
        current_user: UserSchema | None = None,
    ) -> User:
        """Создать нового пользователя."""
        await self._validate_create_data(user_data, current_user)

        user_to_db = UserCreate(
            **user_data.model_dump(exclude={'password'}),
            password_hash=self.security.get_password_hash(user_data.password),
        )

        user = await self.repo.create(user_to_db)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def update_user(
        self,
        user_id: int,
        user_data: UserUpdateRequest,
        current_user: UserSchema,
    ) -> User:
        """Обновить пользователя."""
        await self._check_permission(current_user, user_id)
        await self._validate_update_data(user_data, current_user, user_id)

        user_to_db = UserUpdate(**user_data.model_dump())

        user = await self.repo.update(user_id, user_to_db)
        await self.session.flush()
        await self.session.refresh(user)
        return user

    async def delete_user(self, user_id: int, current_user: UserSchema) -> None:
        """Удалить пользователя."""
        await self._check_permission(current_user, user_id)

        await self.repo.delete(user_id)
        await self.session.flush()

    async def _validate_create_data(
        self,
        user_data: UserCreateRequest,
        current_user: UserSchema | None = None,
    ) -> None:
        """Валидация данных для создания пользователя."""
        # Проверка правильности роли
        if current_user and user_data.role.priority >= current_user.role.priority:
            raise ValidationError('Нельзя назначать права, равные или превышающие ваши')

        if not current_user and user_data.role != UserRole.USER:
            raise ValidationError('Неверные права для пользователя: превышает USER')

        # Проверка уникальности email
        if await self.repo.exists_by(User.email == user_data.email):
            raise ConflictError(f'Пользователь с email {user_data.email} уже существует')

    async def _validate_update_data(
        self,
        user_data: UserUpdateRequest,
        current_user: UserSchema,
        user_id: int,
    ) -> None:
        """Валидация данных для обновления пользователя."""
        # Проверка правильности роли
        if user_id == current_user.id and user_data.role.priority <= current_user.role.priority:
            return

        if user_data.role.priority >= current_user.role.priority:
            raise ValidationError('Нельзя назначать права, равные или превышающие ваши')

    async def update_user_activity(self, user_id:int) -> None:
        """Обновить метрики активности пользователя."""
        await self.repo.update_activity(user_id)

    async def _check_permission(self, current_user: UserSchema, target_user_id: int) -> None:
        """Проверка прав доступа к пользователю."""
        target_user = await self.repo.get(target_user_id)
        if not target_user:
            raise NotFoundError('Пользователь не найден')

        if current_user.id == target_user.id:
            return
        if current_user.role.priority > target_user.role.priority:
            return

        raise PermissionDeniedError('Недостаточно прав для изменения пользователя')
