"""Профиль пользователя.

Все эндпоинты требуют валидный access token
"""

# TODO: Смена пароля
# TODO: CRUD для сессий


from fastapi import APIRouter, Request
from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.dependencies import AuthServiceDep, CurrentUser
from app.schemas import RefreshTokenRequest

router = APIRouter(tags=['User | Profile'], responses=responses(401, 429, 500))


@router.delete('/logout', status_code=204, responses=responses(400, 404))
@limiter.limit('5/hour')
@handle_errors('Ошибка выхода пользователя')
async def logout(
    request: Request,
    request_data: RefreshTokenRequest,
    auth_service: AuthServiceDep,
) -> None:
    """Выход из системы (инвалидирует refresh token)."""
    await auth_service.logout(request_data.token)


@router.delete('/logout-all', status_code=204, responses=responses(404))
@limiter.limit('5/hour')
@handle_errors('Ошибка при выходе из всех устройств пользователя')
async def logout_all(
    request: Request,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> None:
    """Выход из системы на всех устройствах (инвалидирует refresh tokens)."""
    await auth_service.logout_all(current_user.id)
