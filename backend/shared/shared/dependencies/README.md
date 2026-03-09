# Shared Dependencies

Common FastAPI dependencies for services.

## Auth

```python
from shared.dependencies import auth

# Create
deps = auth.create_dependencies()

CurrentUser = deps.CurrentUser
CurrentUserOrNone = deps.CurrentUserOrNone

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
from app.core import AsyncSessionLocal

# Create
deps = db.create_dependencies(AsyncSessionLocal)
get_session = deps.get_session
DBSession = deps.DBSession

# Use in endpoints
@router.get("/users")
async def get_users(session: DBSession):
    ...

# Or use context manager directly
async with get_session() as session:
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
