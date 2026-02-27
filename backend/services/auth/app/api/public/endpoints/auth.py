"""Аутентификация пользователей.

Все эндпоинты логируют сессию (IP, User-Agent)
и обновляют время последней активности пользователя.
"""

from fastapi import APIRouter, BackgroundTasks, Request
from shared.api import responses
from shared.exceptions import handle_errors
from shared.rate_limit import limiter

from app.dependencies import AuthServiceDep, SessionServiceDep, UserServiceDep
from app.schemas import RefreshTokenRequest, TokensResponse, UserCreateRequest, UserLogin

router = APIRouter(tags=['Authentication'], responses=responses(429, 500))


@router.post('/register', status_code=201, responses=responses(400, 409))
@limiter.limit('5/hour')
@handle_errors('Ошибка при регистрации пользователя')
async def register(
    user_data: UserCreateRequest,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    session_service: SessionServiceDep,
) -> TokensResponse:
    """Регистрация нового пользователя."""
    tokens, user_id, token_id = await auth_service.register(user_data)

    bg_tasks.add_task(session_service.create_session, user_id, token_id, request)
    bg_tasks.add_task(user_service.update_user_activity, user_id)

    return tokens


@router.post('/login', responses=responses(400, 401))
@limiter.limit('5/minute')
@handle_errors('Ошибка при входе пользователя')
async def login(
    user_data: UserLogin,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    session_service: SessionServiceDep,
) -> TokensResponse:
    """Вход зарегистрированного пользователя."""
    tokens, user_id, token_id = await auth_service.login(user_data)

    bg_tasks.add_task(session_service.create_session, user_id, token_id, request)
    bg_tasks.add_task(user_service.update_user_activity, user_id)

    return tokens


@router.post('/refresh', responses=responses(400, 401))
@limiter.limit('5/minute')
@handle_errors('Ошибка обновления токенов пользователя')
async def refresh_tokens(
    request_data: RefreshTokenRequest,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: UserServiceDep,
    auth_service: AuthServiceDep,
    session_service: SessionServiceDep,
) -> TokensResponse:
    """Обновление токенов авторизации."""
    tokens, user_id, token_id = await auth_service.refresh_tokens(request_data.token)

    bg_tasks.add_task(session_service.update_session, token_id, request)
    bg_tasks.add_task(user_service.update_user_activity, user_id)

    return tokens
