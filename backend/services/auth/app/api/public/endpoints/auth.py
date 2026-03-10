"""Аутентификация пользователей.

Все эндпоинты логируют сессию (IP, User-Agent)
и обновляют время последней активности пользователя.
"""

from fastapi import APIRouter, BackgroundTasks, Request
from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core import settings
from app.dependencies import AuthServiceDep
from app.schemas import RefreshTokenRequest, TokensResponse, UserLogin, UserRegister

router = APIRouter(tags=['Authentication'], responses=responses(429, 500))


@router.post('/register', status_code=201, responses=responses(400, 409))
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка при регистрации пользователя')
async def register(
    data: UserRegister,
    request: Request,
    bg_tasks: BackgroundTasks,
    auth: AuthServiceDep,
) -> TokensResponse:
    """Регистрация нового пользователя."""
    result = await auth.register(data)

    bg_tasks.add_task(auth.session_service.create, result.refresh_token_id, result.user_id)
    bg_tasks.add_task(auth.user_service.update_activity, result.user_id)

    return result.tokens


@router.post('/login', responses=responses(400, 401))
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка при входе пользователя')
async def login(
    data: UserLogin,
    request: Request,
    bg_tasks: BackgroundTasks,
    auth: AuthServiceDep,
) -> TokensResponse:
    """Вход зарегистрированного пользователя."""
    result = await auth.login(data)

    bg_tasks.add_task(auth.session_service.create, result.refresh_token_id, result.user_id)
    bg_tasks.add_task(auth.user_service.update_activity, result.user_id)

    return result.tokens


@router.post('/refresh', responses=responses(400, 401))
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка обновления токенов пользователя')
async def refresh_tokens(
    data: RefreshTokenRequest,
    request: Request,
    bg_tasks: BackgroundTasks,
    auth: AuthServiceDep,
) -> TokensResponse:
    """Обновление токенов авторизации."""
    result = await auth.refresh_tokens(data)

    bg_tasks.add_task(auth.session_service.update, result.refresh_token_id)
    bg_tasks.add_task(auth.user_service.update_activity, result.user_id)

    return result.tokens
