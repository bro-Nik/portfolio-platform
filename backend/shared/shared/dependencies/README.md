# Shared Dependencies

Common FastAPI dependencies for services.

## Auth

```python
from shared.dependencies import auth
from app.core import settings

# Create
deps = auth.create_dependencies(
    jwt_secret=settings.jwt_secret,
    jwt_algorithm=settings.jwt_algorithm,
)

CurrentUser = deps.CurrentUser

require_admin = deps.require_admin
require_user = deps.require_user

# Use in endpoints
@router.get("/users")
async def get_users(current_user: CurrentUser):

# Use in routers
admin_router = APIRouter(dependencies=[require_admin])
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
