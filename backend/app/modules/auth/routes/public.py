from fastapi import APIRouter, BackgroundTasks, Request

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.auth.dependencies import AuthServiceDep, require_user
from app.common.schemas import AuthUser
from app.modules.auth.schemas import RefreshTokenRequest, TokensResponse, UserLogin, UserRegister
from typing import Annotated


router = APIRouter()


@router.post('/register', status_code=201)
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка регистрации')
async def register(
    data: UserRegister,
    request: Request,
    bg_tasks: BackgroundTasks,
    auth: AuthServiceDep,
) -> TokensResponse:
    result = await auth.register(data)
    bg_tasks.add_task(auth.session_service.create, result.refresh_token_id, result.user_id)
    bg_tasks.add_task(auth.user_service.update_activity, result.user_id)
    return result.tokens


@router.post('/login')
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка входа')
async def login(
    data: UserLogin,
    request: Request,
    bg_tasks: BackgroundTasks,
    auth: AuthServiceDep,
) -> TokensResponse:
    result = await auth.login(data)
    bg_tasks.add_task(auth.session_service.create, result.refresh_token_id, result.user_id)
    bg_tasks.add_task(auth.user_service.update_activity, result.user_id)
    return result.tokens


@router.post('/refresh')
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка обновления токена')
async def refresh_tokens(
    data: RefreshTokenRequest,
    request: Request,
    bg_tasks: BackgroundTasks,
    auth: AuthServiceDep,
) -> TokensResponse:
    result = await auth.refresh_tokens(data)
    bg_tasks.add_task(auth.session_service.update, result.refresh_token_id)
    bg_tasks.add_task(auth.user_service.update_activity, result.user_id)
    return result.tokens


@router.post('/logout', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка выхода')
async def logout(
    data: RefreshTokenRequest,
    request: Request,
    auth: AuthServiceDep,
) -> None:
    await auth.logout(data.token)


@router.post('/logout-all', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка выхода со всех устройств')
async def logout_all(
    request: Request,
    auth: AuthServiceDep,
    _: Annotated[AuthUser, require_user],
) -> None:
    await auth.logout_all()
