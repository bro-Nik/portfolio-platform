from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exporting import fetch_all, model_rows
from app.modules.auth.protocols import ExportAccumulator, UserDataCollector
from app.modules.tags.models import Tag, Taggable


class TagDataCollector(UserDataCollector):
    """Разделы тегов и их привязок к сущностям."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def collect(self, user_id: int, acc: ExportAccumulator) -> None:
        tags = await fetch_all(self._session, Tag, Tag.user_id == user_id)
        taggables = await fetch_all(self._session, Taggable, Taggable.tag_id.in_([t.id for t in tags])) if tags else []
        acc.sections['tags'] = model_rows(tags)
        acc.sections['taggable'] = model_rows(taggables)
