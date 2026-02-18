"""Аутентификация пользователей.

Все эндпоинты логируют сессию (IP, User-Agent)
и обновляют время последней активности пользователя.
"""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, Request

from app.core.exceptions import service_exception_handler
from app.core.rate_limit import limiter
from app.core.responses import POST_RESPONSES
from app.dependencies import get_auth_service, get_session_service, get_user_service
from app.schemas import RefreshTokenRequest, TokensResponse, UserCreateRequest, UserLogin
from app.services.auth import AuthService
from app.services.session import SessionService
from app.services.user import UserService

router = APIRouter(tags=['Authentication'])


@router.post('/register', status_code=201, responses=POST_RESPONSES)
@limiter.limit('5/hour')
@service_exception_handler('Ошибка при регистрации пользователя')
async def register(
    user_data: UserCreateRequest,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> TokensResponse:
    """Регистрация нового пользователя."""
    tokens, user_id, token_id = await auth_service.register(user_data)

    bg_tasks.add_task(session_service.create_session, user_id, token_id, request)
    bg_tasks.add_task(user_service.update_user_activity, user_id)

    return tokens


@router.post('/login', responses=POST_RESPONSES)
@limiter.limit('5/minute')
@service_exception_handler('Ошибка при входе пользователя')
async def login(
    user_data: UserLogin,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> TokensResponse:
    """Вход зарегистрированного пользователя."""
    tokens, user_id, token_id = await auth_service.login(user_data)

    bg_tasks.add_task(session_service.create_session, user_id, token_id, request)
    bg_tasks.add_task(user_service.update_user_activity, user_id)

    return tokens


@router.post('/refresh', responses=POST_RESPONSES)
@limiter.limit('5/minute')
@service_exception_handler('Ошибка обновления токенов пользователя')
async def refresh_tokens(
    request_data: RefreshTokenRequest,
    request: Request,
    bg_tasks: BackgroundTasks,
    user_service: Annotated[UserService, Depends(get_user_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    session_service: Annotated[SessionService, Depends(get_session_service)],
) -> TokensResponse:
    """Обновление токенов авторизации."""
    tokens, user_id, token_id = await auth_service.refresh_tokens(request_data.token)

    bg_tasks.add_task(session_service.update_session, token_id, request)
    bg_tasks.add_task(user_service.update_user_activity, user_id)

    return tokens
