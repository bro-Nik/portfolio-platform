# Shared Dependencies

Common FastAPI dependencies for services.

## Auth

```python
from shared.dependencies import auth
from shared.schemas import AuthUser, UserRole
from app.core.config import settings

# Create
get_current_user = auth.create_auth_dependency(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)

require_user = auth.create_role_requirement(UserRole.USER)
require_admin = auth.create_role_requirement(UserRole.ADMIN)

CurrentUser = Annotated[AuthUser, get_current_user]
RequireUser = Annotated[None, require_user]
RequireAdmin = Annotated[None, require_admin]

# Use in endpoints
@router.get("/users")
async def get_users(current_user: CurrentUser):
    ...
```


## Database

```python
from shared.dependencies import db
from app.core.database import AsyncSessionLocal

# Create
get_db = db.create_session_dependency(AsyncSessionLocal)
DBSession = Annotated[AsyncSession, get_db]

# Use in endpoints
@router.get("/users")
async def get_users(db: DBSession):
    ...

# Or use context manager directly
from shared.dependencies.db import session_scope

async with session_scope(AsyncSessionLocal) as session:
    user = await repo.get(user_id)
```
