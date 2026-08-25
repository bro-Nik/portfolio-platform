from dishka import FromDishka

from .di import AuthProvider
from app.common.dependencies import require_admin, require_user
from app.modules.auth.services.auth import AuthService
from app.modules.auth.services.session import SessionService
from app.modules.auth.services.user import UserService

AuthServiceDep = FromDishka[AuthService]
UserServiceDep = FromDishka[UserService]
SessionServiceDep = FromDishka[SessionService]

__all__ = [
    'AuthProvider',
    'AuthServiceDep',
    'SessionServiceDep',
    'UserServiceDep',
    'require_admin',
    'require_user',
]
