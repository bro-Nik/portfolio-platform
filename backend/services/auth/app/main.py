from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared.rate_limit import setup_rate_limiter

from app.api.admin import admin_router
from app.api.public import public_router
from app.api.user import user_router
from app.core.config import settings

app = FastAPI(
    title='Auth Service API',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
    root_path='/auth',
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_rate_limiter(app, settings.redis_url)
    yield


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
