from typing import Annotated

from fastapi import Request, Response

from app.common.dependencies import CurrentUser, CurrentUserOrNone
from app.common.exceptions import AuthenticationError, handle_errors
from app.common.routing import DishkaRouter
from app.common.schemas import AuthUser
from app.core import settings
from app.core.rate_limit import limiter
from app.modules.auth.dependencies import AuthServiceDep, SessionServiceDep, UserServiceDep, require_user
from app.modules.auth.schemas import (
    AccessTokenResponse,
    DeleteAccountRequest,
    EmailChangeRequest,
    ForgotPasswordRequest,
    LoginSessionResponse,
    PasswordChangeRequest,
    RefreshTokenRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.modules.auth.services.auth import RegisterTaskData
from app.modules.auth.tasks import (
    send_password_reset_confirmation_email,
    send_password_reset_email,
    send_verification_email,
)

router = DishkaRouter()

REFRESH_COOKIE_NAME = 'refresh_token'
REFRESH_COOKIE_PATH = '/auth'
_DAY_SECONDS = 86400


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=settings.jwt_refresh_token_expire_days * _DAY_SECONDS,
        httponly=True,
        secure=settings.env == 'production',
        samesite='strict',
        path=REFRESH_COOKIE_PATH,
    )


def _refresh_token_from_cookie(request: Request) -> str:
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not token:
        raise AuthenticationError('Refresh токен отсутствует')
    return token


@router.post('/register', status_code=201)
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка регистрации')
async def register(
    data: UserRegister,
    request: Request,
    response: Response,
    auth: AuthServiceDep,
) -> AccessTokenResponse:
    result = await auth.register(data)
    await send_verification_email.kiq(result.email, result.verification_token)
    _set_refresh_cookie(response, result.tokens.refresh_token)
    return AccessTokenResponse(access_token=result.tokens.access_token)


@router.post('/login')
@limiter.limit(settings.rate_limit_public)
@handle_errors('Ошибка входа')
async def login(
    data: UserLogin,
    request: Request,
    response: Response,
    auth: AuthServiceDep,
) -> AccessTokenResponse:
    result = await auth.login(data)
    _set_refresh_cookie(response, result.tokens.refresh_token)
    return AccessTokenResponse(access_token=result.tokens.access_token)


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
    user_service: UserServiceDep,
    current_user: CurrentUserOrNone = None,
) -> RegisterResponse:
    if current_user:
        user = await user_service.get_for_auth(id=current_user.id)
        email = user.email
    else:
        email = data.email
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
    request: Request,
    response: Response,
    auth: AuthServiceDep,
) -> AccessTokenResponse:
    token = _refresh_token_from_cookie(request)
    result = await auth.refresh_tokens(RefreshTokenRequest(token=token))
    _set_refresh_cookie(response, result.tokens.refresh_token)
    return AccessTokenResponse(access_token=result.tokens.access_token)


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
    user = await auth.reset_password(data.token, data.password)
    await send_password_reset_confirmation_email.kiq(user.email)
    return RegisterResponse(message='Пароль успешно сброшен')


@router.get('/me')
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка получения профиля')
async def get_me(
    request: Request,
    user_service: UserServiceDep,
    current_user: CurrentUser,
) -> UserResponse:
    user = await user_service.get_detailed(current_user.id)
    return UserResponse.model_validate(user)


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


@router.put('/email', status_code=200)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка смены email')
async def change_email(
    data: EmailChangeRequest,
    request: Request,
    user_service: UserServiceDep,
    current_user: Annotated[AuthUser, require_user],
) -> RegisterResponse:
    token = await user_service.change_email(current_user.id, data)
    if token:
        await send_verification_email.kiq(data.new_email, token)
        return RegisterResponse(message='Письмо с подтверждением отправлено на новый адрес')
    return RegisterResponse(message='Email успешно изменён')


@router.post('/logout', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка выхода')
async def logout(
    request: Request,
    response: Response,
    auth: AuthServiceDep,
) -> None:
    token = request.cookies.get(REFRESH_COOKIE_NAME)
    if token:
        await auth.logout(token)
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


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


@router.delete('/account', status_code=204)
@limiter.limit(settings.rate_limit_auth)
@handle_errors('Ошибка удаления аккаунта')
async def delete_account(
    data: DeleteAccountRequest,
    request: Request,
    auth: AuthServiceDep,
    current_user: Annotated[AuthUser, require_user],
) -> None:
    await auth.delete_account(current_user.id, data)
