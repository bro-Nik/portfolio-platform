from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from slowapi.middleware import SlowAPIMiddleware

from app.common.redis import create_redis
from app.core import settings
from app.core.database import async_engine
from app.core.rate_limit import setup_rate_limiter
from app.di import build_web_container
from app.modules.auth.routes import router as auth_router
from app.modules.market.routes import router as market_router
from app.modules.portfolios.routes import router as portfolios_router
from app.modules.tags.routes import router as tags_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_rate_limiter(app, settings.redis_url)
    yield
    await app.state.dishka_container.close()


container = build_web_container()

app = FastAPI(
    title='Portfolios API',
    description='Portfolios management system',
    version='1.0.0',
    docs_url=None if settings.is_prod else '/docs',
    redoc_url=None if settings.is_prod else '/redoc',
    openapi_url=None if settings.is_prod else '/openapi.json',
    lifespan=lifespan,
)

app.add_middleware(SlowAPIMiddleware)
setup_dishka(container=container, app=app)

logger = logging.getLogger(__name__)

static_dir = Path(__file__).parent.parent / 'static'
if static_dir.exists():
    app.mount('/market/static', StaticFiles(directory=str(static_dir)), name='market_static')


@app.middleware('http')
async def add_cache_headers(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
    response = await call_next(request)
    if request.url.path.startswith('/market/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
    elif request.method == 'GET' and request.url.path.startswith('/market/api/tickers'):
        response.headers['Cache-Control'] = 'public, max-age=60'
    return response


@app.get('/', tags=['root'])
async def service_info() -> dict:
    return {
        'message': 'Portfolios API',
        'version': '1.0.0',
        'docs': '/docs',
        'redoc': '/redoc',
    }


@app.get('/health', tags=['health'])
async def health() -> dict:
    """Liveness: процесс отвечает.

    Зависимости не проверяются намеренно: иначе перезапуск в контейнере
    начнёт циклиться при кратковременной недоступности БД.
    """
    return {'status': 'ok'}


@app.get('/ready', tags=['health'])
async def ready(response: Response) -> dict:
    """Readiness: можно ли принимать трафик.

    Проверяет БД и Redis. Прежний единственный /health всегда возвращал ok, и
    backend числился здоровым при упавшем Postgres — Docker не перезапускал
    его, а nginx продолжал слать запросы в пустоту.
    """
    from sqlalchemy import text

    checks: dict[str, str] = {}
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text('SELECT 1'))
        checks['database'] = 'ok'
    except Exception as exc:
        logger.exception('Проверка БД не пройдена')
        checks['database'] = f'error: {type(exc).__name__}'

    try:
        client = create_redis()
        try:
            await client.ping()
        finally:
            await client.aclose()
        checks['redis'] = 'ok'
    except Exception as exc:
        logger.exception('Проверка Redis не пройдена')
        checks['redis'] = f'error: {type(exc).__name__}'

    is_ready = all(value == 'ok' for value in checks.values())
    if not is_ready:
        response.status_code = 503
    return {'status': 'ok' if is_ready else 'unavailable', 'checks': checks}


app.include_router(auth_router, prefix='/auth', tags=['Auth'])
app.include_router(portfolios_router, prefix='/api', tags=['Portfolios'])
app.include_router(tags_router, prefix='/api', tags=['Tags'])
app.include_router(market_router, prefix='/market', tags=['Market'])
