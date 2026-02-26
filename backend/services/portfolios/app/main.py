from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared.rate_limit import setup_rate_limiter

from app.api import api_router
from app.core.config import settings

app = FastAPI(
    title='Portfolios API',
    description='API for managing user portfolios',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
    root_path='/api',
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_rate_limiter(app, settings.redis_url)
    yield


@app.get('/', tags=['root'])
async def service_info() -> dict:
    """Информация о сервисе."""
    return {
        'message': 'Portfolios API',
        'version': '1.0.0',
        'docs': '/docs',
        'redoc': '/redoc',
    }


app.include_router(api_router)
