from fastapi import APIRouter, Request
from typing import Annotated
from fastapi import Path, Query

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.auth.dependencies import UserServiceDep, AuthServiceDep, require_admin
from app.modules.auth.schemas import (
    UserCreateRequest, UserResponse, UserUpdateRequest, UserRole,
)


router = APIRouter(dependencies=[require_admin])


@router.get('/users')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения пользователей')
async def get_users(
    request: Request,
    user_service: UserServiceDep,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=1000)] = 100,
    search: Annotated[str | None, Query()] = None,
    role: Annotated[UserRole | None, Query()] = None,
) -> list[UserResponse]:
    return await user_service.get_all_detailed(skip, limit, search, role)


@router.get('/users/{user_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения пользователя')
async def get_user(
    request: Request,
    user_id: Annotated[int, Path()],
    user_service: UserServiceDep,
) -> UserResponse:
    return await user_service.get_detailed(user_id)


@router.post('/users', status_code=201)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка создания пользователя')
async def create_user(
    request: Request,
    data: UserCreateRequest,
    user_service: UserServiceDep,
) -> UserResponse:
    user = await user_service.create(data)
    return await user_service.get_detailed(user.id)


@router.put('/users/{user_id}')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка обновления пользователя')
async def update_user(
    request: Request,
    user_id: Annotated[int, Path()],
    data: UserUpdateRequest,
    user_service: UserServiceDep,
) -> UserResponse:
    user = await user_service.update(user_id, data)
    return await user_service.get_detailed(user.id)


@router.delete('/users/{user_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления пользователя')
async def delete_user(
    request: Request,
    user_id: Annotated[int, Path()],
    user_service: UserServiceDep,
) -> None:
    await user_service.delete(user_id)


@router.post('/users/{user_id}/logout-all', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка выхода со всех устройств')
async def logout_all_user(
    request: Request,
    user_id: Annotated[int, Path()],
    auth: AuthServiceDep,
) -> None:
    await auth.logout_all(user_id)
