from typing import Annotated

from fastapi import Depends

from app.common.dependencies import Ctx, DBSession

from app.modules.tags.services.tag import TagService


def get_tag_service(session: DBSession, ctx: Ctx) -> TagService:
    return TagService(session, ctx)


TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
