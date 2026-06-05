"""Теги пользователя."""

from fastapi import APIRouter, Request

from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core import settings
from app.dependencies import TagServiceDep
from app.schemas import TagAttachRequest, TagCreate, TagResponse, TagUpdate

router = APIRouter(prefix='/tags', tags=['Tags'], responses=responses(401, 429, 500))


@router.get('')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении тегов')
async def get_tags(
    request: Request,
    tag_service: TagServiceDep,
) -> list[TagResponse]:
    """Получение всех тегов пользователя."""
    return await tag_service.get_all()


@router.post('', status_code=201, responses=responses(400, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при создании тега')
async def create_tag(
    request: Request,
    data: TagCreate,
    tag_service: TagServiceDep,
) -> TagResponse:
    """Создание нового тега."""
    return await tag_service.create(data.name, data.color)


@router.put('/{tag_id}', responses=responses(400, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при обновлении тега')
async def update_tag(
    request: Request,
    tag_id: int,
    data: TagUpdate,
    tag_service: TagServiceDep,
) -> TagResponse:
    """Обновление тега."""
    return await tag_service.update(tag_id, data.name, data.color)


@router.delete('/{tag_id}', responses=responses(404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при удалении тега')
async def delete_tag(
    request: Request,
    tag_id: int,
    tag_service: TagServiceDep,
) -> dict:
    """Удаление тега."""
    await tag_service.delete(tag_id)
    return {'tag_id': tag_id}


@router.post('/attach', responses=responses(400, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при прикреплении тега')
async def attach_tag(
    request: Request,
    data: TagAttachRequest,
    tag_service: TagServiceDep,
) -> dict:
    """Прикрепить тег к сущности."""
    await tag_service.add_to_entity(data.tag_id, data.entity_type, data.entity_id)
    return {'success': True}


@router.delete('/detach', responses=responses(400, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при откреплении тега')
async def detach_tag(
    request: Request,
    tag_id: int,
    entity_type: str,
    entity_id: int,
    tag_service: TagServiceDep,
) -> dict:
    """Открепить тег от сущности."""
    await tag_service.remove_from_entity(tag_id, entity_type, entity_id)
    return {'success': True}
