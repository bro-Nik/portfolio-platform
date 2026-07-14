from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.auth.models import RefreshToken


class TokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshToken, session)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        return await self.get_by(RefreshToken.token == token)

    async def delete_all_by_user(self, user_id: int) -> int:
        return len(await self.delete_all(RefreshToken.user_id == user_id))
