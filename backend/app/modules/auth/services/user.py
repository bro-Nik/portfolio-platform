from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
from app.common.schemas import Context
from app.core import settings
from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository
from app.modules.auth.schemas import (
    DeleteAccountRequest,
    EmailChangeRequest,
    PasswordChangeRequest,
    UserCreate,
    UserCreateRequest,
    UserRole,
    UserUpdateRequest,
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
        await self.session.commit()
        return user

    async def update(self, id: int, data: UserUpdateRequest) -> User:
        user = await self.get(id)
        await self._validate_update_data(data, user)

        updates: dict = {}
        if data.email is not None and data.email != user.email:
            if await self.repo.exists_by(User.email == data.email):
                raise ConflictError(f'Пользователь с email {data.email} уже существует')
            updates['email'] = data.email
            updates['is_verified'] = True
        if data.password:
            updates['password_hash'] = self.security.get_password_hash(data.password)
        if data.role != user.role:
            updates['role'] = data.role
        if data.status != user.status:
            updates['status'] = data.status

        updated = await self.repo.update(id, updates) if updates else user
        await self.session.commit()
        return updated or user

    async def delete(self, id: int) -> None:
        await self.get(id)
        await self.repo.delete(id)
        await self.session.commit()

    async def update_activity(self, user_id: int) -> None:
        await self.repo.update_activity(user_id)

    async def change_password(self, user_id: int, data: PasswordChangeRequest) -> None:
        user = await self.get(user_id)
        if not self.security.verify_password(data.current_password, user.password_hash):
            raise AuthenticationError('Неверный текущий пароль')
        password_hash = self.security.get_password_hash(data.new_password)
        await self.repo.update(user_id, {'password_hash': password_hash})
        await self.session.commit()

    async def change_email(self, user_id: int, data: EmailChangeRequest) -> str | None:
        user = await self.get(user_id)
        if not self.security.verify_password(data.current_password, user.password_hash):
            raise AuthenticationError('Неверный текущий пароль')
        if await self.repo.exists_by(User.email == data.new_email):
            raise ConflictError(f'Пользователь с email {data.new_email} уже существует')
        if not settings.smtp_enabled:
            await self.repo.update(user_id, {'email': data.new_email, 'is_verified': True})
            await self.session.commit()
            return None
        return self.security.create_email_verification_token(user_id, new_email=data.new_email)

    async def delete_account(self, user_id: int, data: DeleteAccountRequest) -> None:
        user = await self.get(user_id)
        if not self.security.verify_password(data.current_password, user.password_hash):
            raise AuthenticationError('Неверный пароль')
        await self.repo.delete(user_id)

    async def forgot_password(self, email: str) -> str | None:
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        return self.security.create_password_reset_token(user.id)

    async def reset_password(self, token: str, new_password: str) -> int:
        user_id = self.security.verify_password_reset_token(token)
        user = await self.repo.get(user_id)
        if not user:
            raise AuthenticationError('Пользователь не найден')
        password_hash = self.security.get_password_hash(new_password)
        await self.repo.update(user_id, {'password_hash': password_hash})
        return user_id

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
