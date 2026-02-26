# Rate Limiting

IP-based rate limiting for API protection.


## 🚀 Quick Start

```python
from fastapi import FastAPI
from shared.rate_limit import setup_rate_limiter

app = FastAPI()

# On startup
setup_rate_limiter(
    app,
    redis_url="redis://localhost:6379/0"  # optional, memory if None
)

# In endpoints
from shared.rate_limit import limiter

@app.get("/test")
@limiter.limit("5/minute")
async def test(request: Request):  # 👈 requires request parameter!
    return {"ok": True}
```

## ⚠️ Important

- **Requires `request: Request` parameter** in every endpoint using `@limiter.limit`
- Uses client IP for identification
- Memory storage by default
- Redis storage when `redis_url` provided
