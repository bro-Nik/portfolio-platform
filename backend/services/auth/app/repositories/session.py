from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LoginSession
from app.repositories import BaseRepository
from app.schemas import LoginSessionCreate, LoginSessionUpdate


class SessionRepository(
    BaseRepository[LoginSession, LoginSessionCreate, LoginSessionUpdate],
):
    """Репозиторий для работы с сессиями входа пользователя."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LoginSession, session)

    async def get_by_token_id(self, token_id: int) -> LoginSession | None:
        """Получить сессию по ID refresh токена."""
        return await self.get_by(LoginSession.refresh_token_id == token_id)
