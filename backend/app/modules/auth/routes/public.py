from fastapi import APIRouter, BackgroundTasks, Request

from app.common.exceptions import handle_errors
from app.core.rate_limit import limiter

from app.core import settings
from app.modules.auth.dependencies import AuthServiceDep, SessionServiceDep, UserServiceDep, require_user
from app.common.schemas import AuthUser
from app.common.dependencies import CurrentUserOrNone
from app.modules.auth.schemas import (
    EmailChangeRequest, ForgotPasswordRequest, LoginSessionResponse, PasswordChangeRequest,
    RefreshTokenRequest, RegisterResponse, ResetPasswordRequest, ResendVerificationRequest,
    TokensResponse, UserLogin, UserRegister,
)
from app.modules.auth.services.auth import RegisterTaskData
from app.modules.auth.tasks import (
    send_password_reset_confirmation_email,
    send_password_reset_email,
    send_verification_email,
)
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
    await send_verification_email.kiq(result.email, result.verification_token)
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


@router.post('/verify-email')
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка подтверждения email')
async def verify_email(
    data: RefreshTokenRequest,
    request: Request,
    auth: AuthServiceDep,
) -> RegisterResponse:
    return await auth.verify_email(data.token)


@router.post('/resend-verification')
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка повторной отправки')
async def resend_verification(
    data: ResendVerificationRequest,
    request: Request,
    auth: AuthServiceDep,
    current_user: CurrentUserOrNone = None,
) -> RegisterResponse:
    email = current_user.email if current_user else data.email
    if not email:
        return RegisterResponse(message='Email не указан')
    result = await auth.resend_verification(email)
    if isinstance(result, RegisterTaskData):
        await send_verification_email.kiq(result.email, result.token)
    return result if isinstance(result, RegisterResponse) else RegisterResponse(message=result.message)


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


@router.post('/forgot-password')
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка восстановления пароля')
async def forgot_password(
    data: ForgotPasswordRequest,
    request: Request,
    user_service: UserServiceDep,
) -> RegisterResponse:
    token = await user_service.forgot_password(data.email)
    if token:
        await send_password_reset_email.kiq(data.email, token)
    return RegisterResponse(message='Если email зарегистрирован, мы отправили ссылку для сброса пароля')


@router.post('/reset-password')
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка сброса пароля')
async def reset_password(
    data: ResetPasswordRequest,
    request: Request,
    auth: AuthServiceDep,
) -> RegisterResponse:
    user_id = await auth.user_service.reset_password(data.token, data.password)
    user = await auth.user_service.get_for_auth(id=user_id)
    await auth.logout_all(user_id)
    await send_password_reset_confirmation_email.kiq(user.email)
    return RegisterResponse(message='Пароль успешно сброшен')


@router.put('/password', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка смены пароля')
async def change_password(
    data: PasswordChangeRequest,
    request: Request,
    user_service: UserServiceDep,
    current_user: Annotated[AuthUser, require_user],
) -> None:
    await user_service.change_password(current_user.id, data)


@router.put('/email', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка смены email')
async def change_email(
    data: EmailChangeRequest,
    request: Request,
    user_service: UserServiceDep,
    current_user: Annotated[AuthUser, require_user],
) -> None:
    token = await user_service.change_email(current_user.id, data)
    await send_verification_email.kiq(data.new_email, token)


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


@router.get('/sessions')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения сессий')
async def get_sessions(
    request: Request,
    session_service: SessionServiceDep,
    current_user: Annotated[AuthUser, require_user],
) -> list[LoginSessionResponse]:
    return await session_service.get_user_sessions(current_user.id)


@router.delete('/sessions/{session_id}', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления сессии')
async def delete_session(
    request: Request,
    session_id: int,
    session_service: SessionServiceDep,
    current_user: Annotated[AuthUser, require_user],
) -> None:
    await session_service.delete_session(session_id, current_user.id)
