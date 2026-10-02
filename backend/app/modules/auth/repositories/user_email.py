from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User


class UserEmailRepository:
    """Реализация watchlist.protocols.UserEmailReader на таблице users."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_emails(self, user_ids: list[int]) -> dict[int, str]:
        if not user_ids:
            return {}
        result = await self._session.execute(
            select(User.id, User.email).where(
                User.id.in_(user_ids),
                User.is_active.is_(True),
                User.is_verified.is_(True),
            )
        )
        return {row[0]: row[1] for row in result.all()}
