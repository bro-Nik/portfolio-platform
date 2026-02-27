from typing import Annotated

from shared.dependencies import auth

from app.core import settings
from app.schemas import AuthUser, UserRole

get_current_user = auth.create_auth_dependency(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)
require_user = auth.create_role_requirement(UserRole.USER)
require_admin = auth.create_role_requirement(UserRole.ADMIN)

CurrentUser = Annotated[AuthUser, get_current_user]
RequireUser = Annotated[None, require_user]
RequireAdmin = Annotated[None, require_admin]
