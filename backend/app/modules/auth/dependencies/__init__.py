from dishka import FromDishka

from .di import AuthProvider
from app.common.dependencies import require_admin, require_user
from app.modules.auth.protocols import UserDataCollector
from app.modules.auth.services.auth import AuthService
from app.modules.auth.services.session import SessionService
from app.modules.auth.services.user import UserService

AuthServiceDep = FromDishka[AuthService]
UserServiceDep = FromDishka[UserService]
SessionServiceDep = FromDishka[SessionService]
UserDataCollectorDep = FromDishka[UserDataCollector]

__all__ = [
    'AuthProvider',
    'AuthServiceDep',
    'SessionServiceDep',
    'UserDataCollectorDep',
    'UserServiceDep',
    'require_admin',
    'require_user',
]
