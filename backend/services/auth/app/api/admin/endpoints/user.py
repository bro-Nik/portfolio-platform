"""Управление пользователями.

Все эндпоинты требуют валидный access token с ролью ADMIN
"""

from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core import settings
from app.dependencies import AuthServiceDep, CurrentUser, UserServiceDep
from app.schemas import UserCreateRequest, UserResponse, UserRole, UserUpdateRequest

router = APIRouter(prefix='/users', tags=['Admin | Users'], responses=responses(401, 429, 500))


@router.get('/')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении пользователей')
async def get_users(
    request: Request,
    user_service: UserServiceDep,
    skip: Annotated[int, Query(ge=0, description='Количество записей для пропуска')] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description='Лимит записей')] = 100,
    search: Annotated[str | None, Query(description='Поиск по email')] = None,
    role: Annotated[UserRole | None, Query(description='Фильтр по роли')] = None,
) -> list[UserResponse]:
    """Получить список пользователей с пагинацией и фильтрацией."""
    return await user_service.get_many_detailed(skip, limit, search, role)


@router.get('/{user_id}', responses=responses(403, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при получении пользователя')
async def get_user(
    request: Request,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    user_service: UserServiceDep,
) -> UserResponse:
    """Получить пользователя по ID."""
    return await user_service.get_detailed(user_id)


@router.post('/', status_code=201, responses=responses(400, 403, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при создании пользователя')
async def create_user(
    request: Request,
    current_user: CurrentUser,
    data: UserCreateRequest,
    user_service: UserServiceDep,
) -> UserResponse:
    """Создать нового пользователя."""
    user = await user_service.create(data, current_user)
    return await user_service.get_detailed(user.id)


@router.put('/{user_id}', responses=responses(400, 403, 404, 409))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при изменении пользователя')
async def update_user(
    request: Request,
    current_user: CurrentUser,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    data: UserUpdateRequest,
    user_service: UserServiceDep,
) -> UserResponse:
    """Обновить пользователя."""
    user = await user_service.update(user_id, data, current_user)
    return await user_service.get_detailed(user.id)


@router.delete('/{user_id}', status_code=204, responses=responses(400, 403, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при удалении пользователя')
async def delete_user(
    request: Request,
    current_user: CurrentUser,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    user_service: UserServiceDep,
) -> None:
    """Удалить пользователя."""
    await user_service.delete(user_id, current_user)


@router.delete('/{user_id}/logout-all', status_code=204, responses=responses(403, 404))
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка при выходе из всех устройств')
async def logout_all(
    request: Request,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    auth_service: AuthServiceDep,
) -> None:
    """Выход из всех устройств."""
    await auth_service.logout_all(user_id)
