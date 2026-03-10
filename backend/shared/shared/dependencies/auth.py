from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from shared.core import settings
from shared.exceptions import AuthenticationError, ForbiddenException, UnauthorizedException
from shared.schemas import AuthUser, UserRole

security = HTTPBearer(auto_error=False)


@dataclass
class AuthDependencies:
    """Контейнер со всеми зависимостями аутентификации."""
    
    require_user: Callable[..., AuthUser]
    require_admin: Callable[..., AuthUser]
    
    CurrentUser: Annotated[AuthUser, ...]
    CurrentUserOrNone: Annotated[AuthUser | None, ...]


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> AuthUser:
    """Получить текущего пользователя из JWT токена."""
    if not credentials:
        raise UnauthorizedException('Токен доступа отсутствует')

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return AuthUser(**payload)

    except jwt.ExpiredSignatureError as e:
        raise UnauthorizedException('Токен устарел') from e
    except (jwt.InvalidTokenError, ValidationError) as e:
        raise UnauthorizedException('Некорректный токен') from e
    except jwt.PyJWTError as e:
        raise AuthenticationError('Ошибка верификации токена') from e


def get_current_user_or_none(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> AuthUser | None:
    if not credentials:
        return None

    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return AuthUser(**payload)
    except jwt.PyJWTError:
        return None


def create_dependencies() -> AuthDependencies:
    """Фабрика создает все зависимости для работы с аутентификацией."""
       
    def _create_role_requirement(required_role: UserRole) -> Callable[..., AuthUser]:
        """Создать зависимость для проверки конкретной роли."""
        
        def require_role(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
            """Проверить что пользователь имеет требуемую роль и вернуть его."""
            if required_role.priority > current_user.role.priority:
                raise ForbiddenException(f'Требуется роль: {required_role.value}')
            
            return current_user
        
        return Depends(require_role)
    
    require_user = _create_role_requirement(UserRole.USER)
    require_admin = _create_role_requirement(UserRole.ADMIN)
    
    CurrentUser = Annotated[AuthUser, Depends(get_current_user)]
    CurrentUserOrNone = Annotated[AuthUser | None, Depends(get_current_user_or_none)]
    
    return AuthDependencies(
        require_user=require_user,
        require_admin=require_admin,
        CurrentUser=CurrentUser,
        CurrentUserOrNone=CurrentUserOrNone,
    )
