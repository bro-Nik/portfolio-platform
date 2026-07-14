from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.auth.models import LoginSession


class SessionRepository(BaseRepository[LoginSession]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(LoginSession, session)

    async def get_by_token_id(self, token_id: int) -> LoginSession | None:
        return await self.get_by(LoginSession.refresh_token_id == token_id)
