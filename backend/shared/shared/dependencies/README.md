# Shared Dependencies

Common FastAPI dependencies for services.

## Auth

```python
from shared.dependencies import auth
from shared.schemas import AuthUser, UserRole
from app.core.config import settings

get_current_user = auth.create_auth_dependency(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)

require_user = auth.create_role_requirement(UserRole.USER)
require_admin = auth.create_role_requirement(UserRole.ADMIN)

CurrentUser = Annotated[AuthUser, get_current_user]
RequireUser = Annotated[None, require_user]
RequireAdmin = Annotated[None, require_admin]
```



