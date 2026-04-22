# Shared Repositories

Base async CRUD repository for SQLAlchemy.
- `BaseRepository` - async repo

## 🚀 Quick Start

```python
from shared.repositories import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
```
