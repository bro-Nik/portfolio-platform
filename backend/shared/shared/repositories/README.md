# Shared Repositories

Base async CRUD repository for SQLAlchemy.
- `BaseAsyncRepository` - async repo

## 🚀 Quick Start

```python
from shared.repositories import BaseAsyncRepository

class UserRepository(BaseAsyncRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
```
```
