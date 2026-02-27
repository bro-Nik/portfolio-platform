# API Utilities

Common API utilities for services.

## Responses

Helper for consistent error responses in FastAPI.

```python
from fastapi import APIRouter
from shared.api import responses

# In router
router = APIRouter(responses=responses(401, 403, 404))  # common

# In endpoint
@router.post('/', responses=responses(400, 409))  # specific
async def create_user(data: UserCreate):
    ...
```
