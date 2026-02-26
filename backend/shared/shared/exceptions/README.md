# Shared Exceptions

Common exceptions for all services.
- **Business exceptions** - `AuthenticationError`, `NotFoundError`, etc.
- **HTTP exceptions** - `NotFoundException`, `BadRequestException`, etc.
- **Decorator** - `@handle_errors`

## 🚀 Quick Start


```python
from shared.exceptions import NotFoundError, handle_errors

# Business logic
def get_user(id: int):
    if not user:
        raise NotFoundError(f"User {id} not found")

# FastAPI endpoint
@app.get('/users/{id}')
@handle_errors('Error getting user')
async def get_user(id: int):
    return await user_service.get_user(id)
```
