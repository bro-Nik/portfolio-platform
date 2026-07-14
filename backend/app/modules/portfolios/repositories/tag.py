from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.portfolios.models import Tag, Taggable


class TagRepository(BaseRepository[Tag]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Tag, session)

    async def get_by_user(self, user_id: int) -> list[Tag]:
        result = await self._session.execute(select(Tag).where(Tag.user_id == user_id).order_by(Tag.name))
        return list(result.scalars().all())


class TaggableRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_tags(self, entity_type: str, entity_id: int) -> list[Tag]:
        result = await self._session.execute(
            select(Tag).join(Taggable, Tag.id == Taggable.tag_id).where(
                Taggable.entity_type == entity_type, Taggable.entity_id == entity_id,
            ),
        )
        return list(result.scalars().all())

    async def add(self, tag_id: int, entity_type: str, entity_id: int) -> None:
        self._session.add(Taggable(tag_id=tag_id, entity_type=entity_type, entity_id=entity_id))

    async def remove(self, tag_id: int, entity_type: str, entity_id: int) -> None:
        await self._session.execute(
            delete(Taggable).where(Taggable.tag_id == tag_id, Taggable.entity_type == entity_type, Taggable.entity_id == entity_id),
        )

    async def bulk_get_tags(self, items: list[tuple[str, int]]) -> dict[tuple[str, int], list[Tag]]:
        if not items:
            return {}
        conditions = [and_(Taggable.entity_type == t, Taggable.entity_id == i) for t, i in items]
        result = await self._session.execute(
            select(Taggable, Tag).join(Tag, Tag.id == Taggable.tag_id).where(or_(*conditions)),
        )
        grouped: dict[tuple[str, int], list[Tag]] = {}
        for taggable, tag in result.all():
            key = (taggable.entity_type, taggable.entity_id)
            grouped.setdefault(key, []).append(tag)
        return grouped
