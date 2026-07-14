from fastapi import APIRouter, Request

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.portfolios.dependencies import (
    TagServiceDep, require_user,
)
from app.modules.portfolios.schemas import (
    TagAttachRequest, TagCreate, TagResponse, TagUpdate,
)


router = APIRouter(dependencies=[require_user])


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
    return await tag_service.create(data.name, data.color)


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


@router.delete('/tags/{tag_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления тега')
async def delete_tag(
    request: Request,
    tag_id: int,
    tag_service: TagServiceDep,
) -> dict:
    await tag_service.delete(tag_id)
    return {'tag_id': tag_id}


@router.post('/tags/attach')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка прикрепления тега')
async def attach_tag(
    request: Request,
    data: TagAttachRequest,
    tag_service: TagServiceDep,
) -> dict:
    await tag_service.add_to_entity(data.tag_id, data.entity_type, data.entity_id)
    return {'success': True}


@router.delete('/tags/detach')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка открепления тега')
async def detach_tag(
    request: Request,
    tag_id: int,
    entity_type: str,
    entity_id: int,
    tag_service: TagServiceDep,
) -> dict:
    await tag_service.remove_from_entity(tag_id, entity_type, entity_id)
    return {'success': True}
