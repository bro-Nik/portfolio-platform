"""Управление пользователями.

Все эндпоинты требуют валидный access token с ролью ADMIN
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from app.core.exceptions import service_exception_handler
from app.core.rate_limit import limiter
from app.core.responses import DELETE_RESPONSES, GET_RESPONSES, POST_RESPONSES, PUT_RESPONSES
from app.dependencies import get_auth_service, get_user_service
from app.dependencies.auth import get_current_user
from app.schemas import (
    UserCreateRequest,
    UserResponse,
    UserRole,
    UserSchema,
    UserUpdateRequest,
)
from app.services.auth import AuthService
from app.services.user import UserService

router = APIRouter(prefix='/users', tags=['Admin | Users'])


@router.get('/', responses=GET_RESPONSES)
@limiter.limit('5/minute')
@service_exception_handler('Ошибка при получении пользователей')
async def get_users(
    request: Request,
    service: Annotated[UserService, Depends(get_user_service)],
    skip: Annotated[int, Query(ge=0, description='Количество записей для пропуска')] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description='Лимит записей')] = 100,
    search: Annotated[str | None, Query(description='Поиск по email')] = None,
    role: Annotated[UserRole | None, Query(description='Фильтр по роли')] = None,
) -> list[UserResponse]:
    """Получить список пользователей с пагинацией и фильтрацией."""
    return await service.get_users_with_details(skip, limit, search, role)


@router.get('/{user_id}', responses=GET_RESPONSES)
@limiter.limit('5/minute')
@service_exception_handler('Ошибка при получении пользователя')
async def get_user(
    request: Request,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Получить пользователя по ID."""
    return await service.get_user_with_details(user_id)


@router.post('/', status_code=201, responses=POST_RESPONSES)
@limiter.limit('5/minute')
@service_exception_handler('Ошибка при создании пользователя')
async def create_user(
    request: Request,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    user_data: UserCreateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Создать нового пользователя."""
    user = await service.create_user(user_data, current_user)
    return await service.get_user_with_details(user.id)


@router.put('/{user_id}', responses=PUT_RESPONSES)
@limiter.limit('5/minute')
@service_exception_handler('Ошибка при изменении пользователя')
async def update_user(
    request: Request,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    user_data: UserUpdateRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    """Обновить пользователя."""
    user = await service.update_user(user_id, user_data, current_user)
    return await service.get_user_with_details(user.id)


@router.delete('/{user_id}', status_code=204, responses=DELETE_RESPONSES)
@limiter.limit('5/minute')
@service_exception_handler('Ошибка при удалении пользователя')
async def delete_user(
    request: Request,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    service: Annotated[UserService, Depends(get_user_service)],
) -> None:
    """Удалить пользователя."""
    await service.delete_user(user_id, current_user)


@router.delete('/{user_id}/logout-all', status_code=204, responses=DELETE_RESPONSES)
@limiter.limit('5/minute')
@service_exception_handler('Ошибка при выходе из всех устройств')
async def logout_all(
    request: Request,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """Выход из всех устройств."""
    await auth_service.logout_all(user_id)
