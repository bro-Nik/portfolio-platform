from enum import Enum
from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    """Роли пользователей."""

    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    @property
    def priority(self) -> int:
        """Приоритет роли (чем выше, тем больше прав)."""
        return {
            UserRole.USER: 1,
            UserRole.MODERATOR: 2,
            UserRole.ADMIN: 3,
        }.get(self, 1)


class AuthUser(BaseModel):
    """Аутентифицированный пользователь из JWT токена."""

    id: int
    role: UserRole = UserRole.USER
    email: EmailStr | None = None
