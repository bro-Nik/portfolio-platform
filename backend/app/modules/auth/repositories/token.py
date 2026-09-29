from datetime import UTC, datetime

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository
from app.modules.auth.models import RefreshToken


class TokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RefreshToken, session)

    async def get_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        return await self.get_by(RefreshToken.token_hash == token_hash)

    async def delete_all_by_user(self, user_id: int) -> int:
        return len(await self.delete_all(RefreshToken.user_id == user_id))

    async def delete_expired(self) -> int:
        """Удаляет истёкшие refresh-токены.

        Сессии висят на токене по внешнему ключу с ON DELETE CASCADE, поэтому
        вместе с токеном удаляется и запись сессии с её IP и отпечатком
        устройства.
        """
        now = int(datetime.now(UTC).timestamp())
        result = await self._session.execute(delete(RefreshToken).where(RefreshToken.expires_at < now))
        return result.rowcount or 0
