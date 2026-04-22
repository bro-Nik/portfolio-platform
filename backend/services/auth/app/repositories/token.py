from sqlalchemy.ext.asyncio import AsyncSession

from shared.repositories import BaseRepository

from app.models import RefreshToken


class TokenRepository(BaseRepository[RefreshToken]):
    """Репозиторий для работы с Refresh токенами."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshToken, session)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Найти refresh токен по его значению."""
        return await self.get_by(RefreshToken.token == token)

    async def delete_all_by_user(self, user_id: int) -> int:
        """Удалить все refresh токены пользователя."""
        return len(await self.delete_all(RefreshToken.user_id == user_id))
