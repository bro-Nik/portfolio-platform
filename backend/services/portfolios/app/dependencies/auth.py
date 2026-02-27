from typing import Annotated

from shared.dependencies import auth

from app.core import settings
from app.schemas import AuthUser

get_current_user = auth.create_auth_dependency(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)

CurrentUser = Annotated[AuthUser, get_current_user]
