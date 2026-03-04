"""Аутентификация пользователей.

Все эндпоинты логируют сессию (IP, User-Agent)
и обновляют время последней активности пользователя.
"""

from fastapi import APIRouter, BackgroundTasks, Request
from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.core import settings
from app.dependencies import AuthServiceDep, SessionServiceDep, UserServiceDep
from app.schemas import RefreshTokenRequest, TokensResponse, UserLogin, UserRegister

router = APIRouter(tags=['Authentication'], responses=responses(429, 500))


@router.post('/register', status_code=201, responses=responses(400, 409))
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка при регистрации пользователя')
async def register(
    data: UserRegister,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    session_service: SessionServiceDep,
) -> TokensResponse:
    """Регистрация нового пользователя."""
    auth = await auth_service.register(data)

    bg_tasks.add_task(session_service.create, auth.user_id, auth.refresh_token_id, request)
    bg_tasks.add_task(user_service.update_activity, auth.user_id)

    return auth.tokens


@router.post('/login', responses=responses(400, 401))
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка при входе пользователя')
async def login(
    data: UserLogin,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    session_service: SessionServiceDep,
) -> TokensResponse:
    """Вход зарегистрированного пользователя."""
    auth = await auth_service.login(data)

    bg_tasks.add_task(session_service.create, auth.user_id, auth.refresh_token_id, request)
    bg_tasks.add_task(user_service.update_activity, auth.user_id)

    return auth.tokens


@router.post('/refresh', responses=responses(400, 401))
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка обновления токенов пользователя')
async def refresh_tokens(
    data: RefreshTokenRequest,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    session_service: SessionServiceDep,
) -> TokensResponse:
    """Обновление токенов авторизации."""
    auth = await auth_service.refresh_tokens(data)

    bg_tasks.add_task(session_service.update, auth.refresh_token_id, request)
    bg_tasks.add_task(user_service.update_activity, auth.user_id)

    return auth.tokens
