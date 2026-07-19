from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'

    @property
    def priority(self) -> int:
        return {
            UserRole.USER: 1,
            UserRole.MODERATOR: 2,
            UserRole.ADMIN: 3,
        }.get(self, 1)


class AuthUser(BaseModel):
    id: int
    role: UserRole = UserRole.USER
    login: str = ''
