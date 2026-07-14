from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.core.rate_limit import setup_rate_limiter
from slowapi.middleware import SlowAPIMiddleware

from app.core import settings
from app.modules.auth.routes import router as auth_router
from app.modules.portfolios.routes import router as portfolios_router
from app.modules.market.routes import router as market_router
from app.modules.market.dependencies import container


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_rate_limiter(app, settings.redis_url)
    yield
    await container.close()


app = FastAPI(
    title='Portfolios API',
    description='Portfolios management system',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc',
    lifespan=lifespan,
)

app.add_middleware(SlowAPIMiddleware)
setup_dishka(container=container, app=app)

static_dir = Path(__file__).parent.parent / 'static'
if static_dir.exists():
    app.mount('/market/static', StaticFiles(directory=str(static_dir)), name='market_static')


@app.middleware('http')
async def add_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response


@app.get('/', tags=['root'])
async def service_info() -> dict:
    return {
        'message': 'Portfolios API',
        'version': '1.0.0',
        'docs': '/docs',
        'redoc': '/redoc',
    }

# Auth routes
app.include_router(auth_router, prefix='/auth', tags=['Auth'])

# Portfolios routes
app.include_router(portfolios_router, prefix='/api', tags=['Portfolios'])

# Market routes
app.include_router(market_router, prefix='/market', tags=['Market'])
