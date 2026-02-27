from typing import Annotated

from fastapi import Depends
from shared.dependencies import auth

from app.core.config import settings
from app.schemas import AuthUser, UserRole

from .database import get_db_session
from .services import get_auth_service, get_session_service, get_user_service

get_current_user = auth.create_auth_dependency(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)
require_user = auth.create_role_requirement(UserRole.USER)
require_admin = auth.create_role_requirement(UserRole.ADMIN)

CurrentUser = Annotated[AuthUser, get_current_user]
RequireUser = Annotated[None, require_user]
RequireAdmin = Annotated[None, require_admin]
