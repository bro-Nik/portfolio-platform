from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared.exceptions import ForbiddenException, UnauthorizedException
from shared.schemas import AuthUser, UserRole

security = HTTPBearer()


def create_auth_dependency(jwt_secret: str, jwt_algorithm: str = "HS256"):
    """Фабрика зависимости для получения текущего пользователя."""
    
    def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    ) -> AuthUser:
        """Получить текущего пользователя из JWT токена."""
        token = credentials.credentials

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=[jwt_algorithm])

            user_id = payload.get('sub')
            if user_id is None:
                raise UnauthorizedException('Некорректный токен')

            return AuthUser(
                    id=user_id,
                    role=payload.get('role'),
                )

        except jwt.ExpiredSignatureError as e:
            raise UnauthorizedException('Токен устарел') from e
        except jwt.InvalidTokenError as e:
            raise UnauthorizedException('Некорректный токен') from e
    
    return Depends(get_current_user)


def create_role_requirement(required_role: UserRole) -> Callable[[AuthUser], None]:
    """Фабрика для проверки роли пользователя."""

    def require_role(current_user: AuthUser) -> None:
        """Проверить что пользователь имеет требуемую роль."""
        if required_role.priority > current_user.role.priority:
            raise ForbiddenException(f'Требуется роль: {required_role.value}')
    
    return Depends(require_role)
