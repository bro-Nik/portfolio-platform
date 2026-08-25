from fastapi import Request

from app.common.routing import DishkaRouter

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.tags.dependencies import (
    TagServiceDep, require_user,
)
from app.modules.tags.schemas import (
    TagCreate, TagEntityType, TagResponse, TagUpdate,
)


router = DishkaRouter(dependencies=[require_user])


@router.get('/tags')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения тегов')
async def get_tags(
    request: Request,
    tag_service: TagServiceDep,
) -> list[TagResponse]:
    return await tag_service.get_all()


@router.post('/tags', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка создания тега')
async def create_tag(
    request: Request,
    data: TagCreate,
    tag_service: TagServiceDep,
) -> TagResponse:
    return await tag_service.create(data.name, data.color, data.scope)


@router.post('/tags/{tag_id}/entities/{entity_type}/{entity_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка прикрепления тега')
async def attach_tag(
    request: Request,
    tag_id: int,
    entity_type: TagEntityType,
    entity_id: int,
    tag_service: TagServiceDep,
) -> None:
    await tag_service.add_to_entity(tag_id, entity_type, entity_id)


@router.delete('/tags/{tag_id}/entities/{entity_type}/{entity_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка открепления тега')
async def detach_tag(
    request: Request,
    tag_id: int,
    entity_type: TagEntityType,
    entity_id: int,
    tag_service: TagServiceDep,
) -> None:
    await tag_service.remove_from_entity(tag_id, entity_type, entity_id)


@router.put('/tags/{tag_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления тега')
async def update_tag(
    request: Request,
    tag_id: int,
    data: TagUpdate,
    tag_service: TagServiceDep,
) -> TagResponse:
    return await tag_service.update(tag_id, data.name, data.color)


@router.delete('/tags/{tag_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления тега')
async def delete_tag(
    request: Request,
    tag_id: int,
    tag_service: TagServiceDep,
) -> None:
    await tag_service.delete(tag_id)
