from shared.dependencies import auth

from app.core import settings

deps = auth.create_dependencies(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)

CurrentUser = deps.CurrentUser
CurrentUserOrNone = deps.CurrentUserOrNone
