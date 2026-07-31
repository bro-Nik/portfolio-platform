from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import NotFoundError

from app.modules.portfolios.models import Tag
from app.modules.portfolios.repositories import TagRepository, TaggableRepository
from app.common.schemas import Context


class TagService:
    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self._session = session
        self.repo = TagRepository(session)
        self.taggable_repo = TaggableRepository(session)

    async def get_all(self) -> list[Tag]:
        return await self.repo.get_by_user(self.ctx.actor.id)

    async def create(self, name: str, color: str | None = None, scope: str = 'asset') -> Tag:
        tag = await self.repo.create({'name': name, 'color': color, 'scope': scope, 'user_id': self.ctx.actor.id})
        await self._session.flush()
        return tag

    async def update(self, tag_id: int, name: str | None = None, color: str | None = None) -> Tag:
        tag = await self.repo.get(tag_id)
        if not tag or tag.user_id != self.ctx.actor.id:
            raise NotFoundError('Тег не найден')
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if color is not None:
            update_data['color'] = color
        if update_data:
            tag = await self.repo.update(tag_id, update_data)
        return tag

    async def delete(self, tag_id: int) -> None:
        tag = await self.repo.get(tag_id)
        if not tag or tag.user_id != self.ctx.actor.id:
            raise NotFoundError('Тег не найден')
        await self.repo.delete(tag_id)

    async def add_to_entity(self, tag_id: int, entity_type: str, entity_id: int) -> None:
        tag = await self.repo.get(tag_id)
        if not tag or tag.user_id != self.ctx.actor.id:
            raise NotFoundError('Тег не найден')
        await self.taggable_repo.add(tag_id, entity_type, entity_id)

    async def remove_from_entity(self, tag_id: int, entity_type: str, entity_id: int) -> None:
        await self.taggable_repo.remove(tag_id, entity_type, entity_id)
