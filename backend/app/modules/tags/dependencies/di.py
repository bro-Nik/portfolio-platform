from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.schemas import Context
from app.modules.tags.protocols import EntityOwnershipChecker
from app.modules.tags.services.tag import TagService


class TagsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_tag_service(
        self,
        session: AsyncSession,
        ctx: Context,
        ownership: EntityOwnershipChecker,
    ) -> TagService:
        return TagService(session, ctx, ownership=ownership)
