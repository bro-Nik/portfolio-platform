from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def db_session():
    return AsyncMock()


@pytest.fixture
def mock():
    def _create(spec=None, **kwargs):
        mock = MagicMock(spec=spec) if spec else MagicMock()
        mock.configure_mock(**kwargs)
        return mock

    return _create


@pytest.fixture
def async_mock():
    def _create(spec=None, **kwargs):
        mock = AsyncMock(spec=spec) if spec else AsyncMock()
        mock.configure_mock(**kwargs)
        return mock

    return _create


@pytest.fixture
def data():
    def _create(**kwargs):
        obj = SimpleNamespace(**kwargs)
        obj.model_dump = lambda **_: {k: getattr(obj, k) for k in kwargs}
        return obj

    return _create


@pytest.fixture
async def app_client():
    """HTTP-клиент для корневых (не модульных) тестов.

    Интеграционные контесты переопределяют `client` своими фикстурами; здесь
    нужен независимый клиент без подмены DI-контейнера.
    """
    from asgi_lifespan import LifespanManager
    from httpx import ASGITransport, AsyncClient

    from app.main import app as fastapi_app

    async with (
        LifespanManager(fastapi_app) as manager,
        AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url='http://testserver',
            follow_redirects=True,
        ) as client,
    ):
        yield client
