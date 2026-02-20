from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.admin import admin_router
from app.api.public import public_router
from app.api.user import user_router
from app.core.rate_limit import limiter

app = FastAPI(
    title='Auth Service API',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
    root_path='/auth',
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get('/', tags=['root'])
async def service_info() -> dict:
    """Информация о сервисе."""
    return {
        'message': 'Auth Service API',
        'version': '1.0.0',
        'docs': '/docs',
        'redoc': '/redoc',
    }


app.include_router(public_router)
app.include_router(user_router)
app.include_router(admin_router)
