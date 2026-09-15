from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from pydantic import ValidationError

from app.common.exceptions import AuthenticationError, ForbiddenException, UnauthorizedException
from app.common.schemas import AuthUser, UserRole
from app.core import settings

security = HTTPBearer(auto_error=False)

ACCESS_TOKEN_TYPE = 'access'


def _decode_access_token(token: str) -> AuthUser:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    if payload.get('type') != ACCESS_TOKEN_TYPE:
        raise jwt.InvalidTokenError(f'Ожидался токен типа {ACCESS_TOKEN_TYPE}')
    return AuthUser(**payload)


def get_actor_from_headers(authorization: str | None) -> AuthUser | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return None

    try:
        return _decode_access_token(token)
    except (jwt.PyJWTError, ValidationError):
        return None


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> AuthUser:
    if not credentials:
        raise UnauthorizedException('Токен доступа отсутствует')

    token = credentials.credentials
    try:
        return _decode_access_token(token)

    except jwt.ExpiredSignatureError as e:
        raise UnauthorizedException('Токен устарел') from e
    except (jwt.InvalidTokenError, ValidationError) as e:
        raise UnauthorizedException('Некорректный токен') from e
    except jwt.PyJWTError as e:
        raise AuthenticationError('Ошибка верификации токена') from e


def get_current_user_or_none(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> AuthUser | None:
    if not credentials:
        return None
    return get_actor_from_headers(credentials.scheme.lower() + ' ' + credentials.credentials)


def _create_role_requirement(required_role: UserRole) -> Callable[..., AuthUser]:
    def require_role(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
        if required_role.priority > current_user.role.priority:
            raise ForbiddenException(f'Требуется роль: {required_role.value}')
        return current_user

    return Depends(require_role)


require_user = _create_role_requirement(UserRole.USER)
require_admin = _create_role_requirement(UserRole.ADMIN)

CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
CurrentUserOrNone = Annotated[AuthUser | None, Depends(get_current_user_or_none)]
