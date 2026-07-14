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
