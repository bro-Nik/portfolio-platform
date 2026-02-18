from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshToken
from app.repositories import BaseRepository
from app.schemas import RefreshTokenCreate, RefreshTokenUpdate


class TokenRepository(
    BaseRepository[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate],
):
    """Репозиторий для работы с Refresh токенами."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshToken, session)

    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Найти refresh токен по его значению."""
        return await self.get_by(RefreshToken.token == token)

    async def delete_user_tokens(self, user_id: int) -> int:
        """Удалить все refresh токены пользователя."""
        return len(await self.delete_many_by(RefreshToken.user_id == user_id))
