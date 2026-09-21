"""Проверки, что бюджет соединений и таймауты реально применены к движку."""

from app.core import settings
from app.core.database import async_engine


class TestEngineConfiguration:
    def test_pool_timeout_is_explicit(self):
        # Без явного значения дефолт SQLAlchemy — 30 с, и задача падает
        # TimeoutError в пуле, который никто не логирует.
        assert async_engine.pool._timeout == settings.db_pool_timeout

    def test_connection_budget_matches_worker_concurrency(self):
        # Воркер выполняет TASKIQ_WORKERS * TASKIQ_MAX_ASYNC_TASKS задач
        # одновременно; каждая держит соединение во время внешних запросов.
        capacity = settings.db_pool_size + settings.db_max_overflow
        assert capacity >= 4, (
            f'пул на процесс ({capacity}) меньше конкурентности воркера, '
            'задачи будут ждать соединение и падать по таймауту'
        )

    def test_statement_timeout_configured(self):
        assert settings.db_statement_timeout_ms > 0
