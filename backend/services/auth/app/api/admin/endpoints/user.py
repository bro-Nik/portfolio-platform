"""Управление пользователями.

Все эндпоинты требуют валидный access token с ролью ADMIN
"""

from typing import Annotated

from fastapi import APIRouter, Path, Query, Request
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core.responses import DELETE_RESPONSES, GET_RESPONSES, POST_RESPONSES, PUT_RESPONSES
from app.dependencies import AuthServiceDep, CurrentUser, UserServiceDep
from app.schemas import UserCreateRequest, UserResponse, UserRole, UserUpdateRequest

router = APIRouter(prefix='/users', tags=['Admin | Users'])


@router.get('/', responses=GET_RESPONSES)
@limiter.limit('5/minute')
@handle_errors('Ошибка при получении пользователей')
async def get_users(
    request: Request,
    service: UserServiceDep,
    skip: Annotated[int, Query(ge=0, description='Количество записей для пропуска')] = 0,
    limit: Annotated[int, Query(ge=1, le=1000, description='Лимит записей')] = 100,
    search: Annotated[str | None, Query(description='Поиск по email')] = None,
    role: Annotated[UserRole | None, Query(description='Фильтр по роли')] = None,
) -> list[UserResponse]:
    """Получить список пользователей с пагинацией и фильтрацией."""
    return await service.get_users_with_details(skip, limit, search, role)


@router.get('/{user_id}', responses=GET_RESPONSES)
@limiter.limit('5/minute')
@handle_errors('Ошибка при получении пользователя')
async def get_user(
    request: Request,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    service: UserServiceDep,
) -> UserResponse:
    """Получить пользователя по ID."""
    return await service.get_user_with_details(user_id)


@router.post('/', status_code=201, responses=POST_RESPONSES)
@limiter.limit('5/minute')
@handle_errors('Ошибка при создании пользователя')
async def create_user(
    request: Request,
    current_user: CurrentUser,
    user_data: UserCreateRequest,
    service: UserServiceDep,
) -> UserResponse:
    """Создать нового пользователя."""
    user = await service.create_user(user_data, current_user)
    return await service.get_user_with_details(user.id)


@router.put('/{user_id}', responses=PUT_RESPONSES)
@limiter.limit('5/minute')
@handle_errors('Ошибка при изменении пользователя')
async def update_user(
    request: Request,
    current_user: CurrentUser,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    user_data: UserUpdateRequest,
    service: UserServiceDep,
) -> UserResponse:
    """Обновить пользователя."""
    user = await service.update_user(user_id, user_data, current_user)
    return await service.get_user_with_details(user.id)


@router.delete('/{user_id}', status_code=204, responses=DELETE_RESPONSES)
@limiter.limit('5/minute')
@handle_errors('Ошибка при удалении пользователя')
async def delete_user(
    request: Request,
    current_user: CurrentUser,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    service: UserServiceDep,
) -> None:
    """Удалить пользователя."""
    await service.delete_user(user_id, current_user)


@router.delete('/{user_id}/logout-all', status_code=204, responses=DELETE_RESPONSES)
@limiter.limit('5/minute')
@handle_errors('Ошибка при выходе из всех устройств')
async def logout_all(
    request: Request,
    user_id: Annotated[int, Path(..., description='ID пользователя')],
    auth_service: AuthServiceDep,
) -> None:
    """Выход из всех устройств."""
    await auth_service.logout_all(user_id)
