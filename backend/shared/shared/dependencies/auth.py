from collections.abc import Callable
from dataclasses import dataclass
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError

from shared.exceptions import ForbiddenException, UnauthorizedException
from shared.schemas import AuthUser, UserRole

security = HTTPBearer()


@dataclass
class AuthDependencies:
    """Контейнер со всеми зависимостями аутентификации."""
    
    require_user: Callable[..., AuthUser]
    require_admin: Callable[..., AuthUser]
    
    CurrentUser: Annotated[AuthUser, ...]


def create_dependencies(jwt_secret: str, jwt_algorithm: str = 'HS256') -> AuthDependencies:
    """Фабрика создает все зависимости для работы с аутентификацией."""
    
    def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    ) -> AuthUser:
        """Получить текущего пользователя из JWT токена."""
        token = credentials.credentials

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])
            return AuthUser(**payload)

        except jwt.ExpiredSignatureError as e:
            raise UnauthorizedException('Токен устарел') from e
        except (jwt.InvalidTokenError, ValidationError) as e:
            raise UnauthorizedException('Некорректный токен') from e
    
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
    
    return AuthDependencies(
        require_user=require_user,
        require_admin=require_admin,
        CurrentUser=CurrentUser,
    )
