from datetime import UTC, datetime

from shared.repositories import BaseAsyncRepository as BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import User
from app.schemas import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """Репозиторий для работы с пользователями."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> User | None:
        """Найти пользователя по email."""
        return await self.get_by(User.email == email)

    async def update_activity(self, user_id: int) -> None:
        """Обновить метрики активности пользователя."""
        user = await self.get(user_id)
        if user:
            user.last_active_at = datetime.now(UTC)
            user.total_active_time += settings.access_token_expire_minutes * 60

    async def get_many_with_sessions(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        role: str | None = None,
    ) -> list[User]:
        """Получить список пользователей с пагинацией и сессиями."""
        where = []

        # Поиск
        if search:
            where.append(User.email.ilike(f'%{search}%'))

        # Фильтр по роли
        if role:
            where.append(User.role == role)

        return await self.get_many_by(
            *where,
            skip=skip,
            limit=limit,
            order_by=[User.created_at.desc()],
            relations=('login_sessions',),
        )
