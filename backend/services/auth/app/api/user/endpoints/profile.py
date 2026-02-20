"""Профиль пользователя.

Все эндпоинты требуют валидный access token
"""

# TODO: Смена пароля
# TODO: CRUD для сессий


from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.core.exceptions import service_exception_handler
from app.core.rate_limit import limiter
from app.core.responses import DELETE_RESPONSES
from app.dependencies import get_auth_service, get_current_user
from app.schemas import RefreshTokenRequest, UserSchema
from app.services.auth import AuthService

router = APIRouter(tags=['User | Profile'])


@router.delete('/logout', status_code=204, responses=DELETE_RESPONSES)
@limiter.limit('5/hour')
@service_exception_handler('Ошибка выхода пользователя')
async def logout(
    request: Request,
    request_data: RefreshTokenRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """Выход из системы (инвалидирует refresh token)."""
    await auth_service.logout(request_data.token)


@router.delete('/logout-all', status_code=204, responses=DELETE_RESPONSES)
@limiter.limit('5/hour')
@service_exception_handler('Ошибка при выходе из всех устройств пользователя')
async def logout_all(
    request: Request,
    current_user: Annotated[UserSchema, Depends(get_current_user)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    """Выход из системы на всех устройствах (инвалидирует refresh tokens)."""
    await auth_service.logout_all(current_user.id)
