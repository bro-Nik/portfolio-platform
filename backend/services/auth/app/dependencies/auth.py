from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import SecurityService
from app.schemas import UserRole, UserSchema

security = HTTPBearer()


def require_role(required_role: UserRole) -> Callable[[UserSchema], None]:
    """Зависимость для проверки роли пользователя."""
    def role_checker(current_user: Annotated[UserSchema, Depends(get_current_user)]) -> None:
        if required_role.priority > current_user.role.priority:
            raise ForbiddenException(f'Требуется роль доступа: {required_role.value}')
    return role_checker


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UserSchema:
    """Зависимость для получения текущего пользователя по JWT токену."""
    token = credentials.credentials
    payload = SecurityService.verify_token(token)

    user_id = payload.get('sub')
    if user_id is None:
        raise UnauthorizedException('Некорректный токен')

    return UserSchema(
        id=user_id,
        role=payload.get('role'),
    )
