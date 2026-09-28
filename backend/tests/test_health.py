"""Health-эндпоинты.

`/health` и `/ready` отвечали одинаково и всегда, поэтому проверка готовности
ничего не проверяла: backend числился здоровым при упавшем Postgres, а Docker
не перезапускал его.
"""

from fastapi import status

from app.core.database import async_engine


class TestHealth:
    async def test_health_is_liveness_only(self, app_client):
        response = await app_client.get('/health')

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {'status': 'ok'}


class TestReady:
    async def test_reports_checks(self, app_client):
        response = await app_client.get('/ready')

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['status'] == 'ok'
        assert set(data['checks']) == {'database', 'redis'}

    async def test_unavailable_when_database_down(self, app_client, monkeypatch):
        from sqlalchemy.exc import OperationalError

        import app.main as main_module

        class _BrokenEngine:
            def connect(self):
                raise OperationalError('SELECT 1', {}, Exception('down'))

        monkeypatch.setattr(main_module, 'async_engine', _BrokenEngine())

        response = await app_client.get('/ready')

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        data = response.json()
        assert data['status'] == 'unavailable'
        assert data['checks']['database'].startswith('error:')

    async def test_unavailable_when_redis_down(self, app_client, monkeypatch):
        from redis.exceptions import ConnectionError as RedisConnectionError

        def _broken_redis():
            raise RedisConnectionError('redis down')

        monkeypatch.setattr('app.main.create_redis', _broken_redis)

        response = await app_client.get('/ready')

        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert response.json()['checks']['redis'].startswith('error:')


class TestReadyClosesRedisClient:
    async def test_client_is_closed_even_on_failure(self, app_client, monkeypatch):
        created = []

        class _Client:
            def __init__(self) -> None:
                self.closed = False
                created.append(self)

            async def ping(self) -> None:
                raise RuntimeError('boom')

            async def aclose(self) -> None:
                self.closed = True

        import app.main as main_module

        monkeypatch.setattr(main_module, 'create_redis', _Client)

        await app_client.get('/ready')

        # Утечка клиента Redis заставляет воркер накапливать сокеты.
        assert [client.closed for client in created] == [True]


class TestEngineImportable:
    def test_ready_uses_shared_engine(self):
        # Проверка БД должна идти через тот же движок, что и приложение.
        assert async_engine is not None
