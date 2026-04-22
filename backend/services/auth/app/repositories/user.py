from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from shared.repositories import BaseRepository

from app.core import settings
from app.models import User


class UserRepository(BaseRepository[User]):
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(User, session)

    async def get_by_email(self, email: str) -> User | None:
        """Найти пользователя по email."""
        return await self.get_by(User.email == email)

    async def update_activity(self, user_id: int) -> None:
        """Обновить метрики активности пользователя."""
        user = await self.get(user_id)
        if user:
            user.last_active_at = datetime.now(UTC)
            user.total_active_time += settings.jwt_access_token_expire_minutes * 60

    async def get_with_sessions(self, user_id: int) -> User | None:
        """Получить пользователя с сессиями."""
        return await self.get_by(User.id == user_id, relations=('login_sessions',))

    async def get_all_with_sessions(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        role: str | None = None,
    ) -> list[User]:
        """Получить список пользователей с пагинацией и сессиями."""
        where = []

        if search:
            where.append(User.email.ilike(f'%{search}%'))

        if role:
            where.append(User.role == role)

        return await self.get_all(
            *where,
            order=[User.created_at.desc()],
            relations=('login_sessions',),
        )
