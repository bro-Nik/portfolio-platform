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

### Async (FastAPI)

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
from shared.dependencies.db import async_session
from app.core.database import AsyncSessionLocal

async with async_session(AsyncSessionLocal) as session:
    user = await repo.get(user_id)
```

### Sync (Celery)

```python
from shared.dependencies.db import sync_session
from app.core.database import SyncSessionLocal

# Use in Celery tasks
def process_report(report_id: int):
    with sync_session(SyncSessionLocal) as session:
        report = session.query(Report).get(report_id)
        # process report...
```
