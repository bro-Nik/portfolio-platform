from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BusinessRuleError, ConflictError, NotFoundError, PermissionDeniedError
from app.common.schemas import Context

from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from app.modules.auth.schemas import (
    UserCreate, UserCreateRequest, UserUpdate, UserUpdateRequest, UserRole,
)
from app.modules.auth.security import SecurityService


class UserService:
    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.session = session
        self.repo = UserRepository(session)
        self.security = SecurityService()

    async def get(self, id: int) -> User:
        user = await self.repo.get(id)
        self._verify(user)
        return user

    async def get_detailed(self, id: int) -> User:
        user = await self.repo.get_with_sessions(id)
        self._verify(user)
        return user

    async def get_for_auth(self, id: int | None = None, email: str | None = None) -> User:
        user = await self.repo.get(id) if id else await self.repo.get_by_email(email) if email else None
        self._check_exists(user)
        return user

    async def get_all_detailed(self, skip: int = 0, limit: int = 20, search: str | None = None, role: str | None = None) -> list[User]:
        return await self.repo.get_all_with_sessions(skip, limit, search, role)

    async def create(self, data: UserCreateRequest) -> User:
        await self._validate_create_data(data)
        user_to_db = UserCreate(**data.model_dump(exclude={'password'}), password_hash=self.security.get_password_hash(data.password))
        user = await self.repo.create(user_to_db.model_dump())
        await self.session.flush()
        return user

    async def update(self, id: int, data: UserUpdateRequest) -> User:
        user = await self.get(id)
        await self._validate_update_data(data, user)
        user_to_db = UserUpdate(**data.model_dump())
        return await self.repo.update(id, user_to_db.model_dump())

    async def delete(self, id: int) -> None:
        await self.get(id)
        await self.repo.delete(id)

    async def update_activity(self, user_id: int) -> None:
        await self.repo.update_activity(user_id)

    async def _validate_create_data(self, data: UserCreateRequest) -> None:
        if self.ctx.actor_optional and data.role.priority >= self.ctx.actor.role.priority:
            raise BusinessRuleError('Нельзя назначать права, равные или превышающие ваши')
        if not self.ctx.actor_optional and data.role != UserRole.USER:
            raise BusinessRuleError('Неверные права для пользователя: превышает USER')
        if await self.repo.exists_by(User.email == data.email):
            raise ConflictError(f'Пользователь с email {data.email} уже существует')

    async def _validate_update_data(self, data: UserUpdateRequest, user: User) -> None:
        if user.id == self.ctx.actor.id and data.role.priority <= self.ctx.actor.role.priority:
            return
        if data.role.priority >= self.ctx.actor.role.priority:
            raise BusinessRuleError('Нельзя назначать права, равные или превышающие ваши')

    def _verify(self, user: User) -> None:
        self._check_exists(user)
        self._check_permission(user)

    def _check_exists(self, user: User | None) -> None:
        if not user:
            raise NotFoundError('Пользователь не найден')

    def _check_permission(self, user: User) -> None:
        if self.ctx.actor.id == user.id:
            return
        if self.ctx.actor.role.priority > user.role.priority:
            return
        raise PermissionDeniedError('Недостаточно прав')
