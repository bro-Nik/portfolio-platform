# Shared Repositories

Base CRUD repositories for SQLAlchemy.
- `BaseAsyncRepository` - async repo
- `BaseSyncRepository` - sync repo

## 🚀 Quick Start


```python
from shared.repositories import BaseAsyncRepository as BaseRepository     # async
#from shared.repositories import BaseSyncRepository as BaseRepository     # sync

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):  # or Session for sync
        super().__init__(User, session)
```
