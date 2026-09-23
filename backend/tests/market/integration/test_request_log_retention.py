"""Журнал внешних запросов: границы выдачи и уборка старых записей."""

from datetime import UTC, datetime, timedelta

import pytest

from app.modules.market.models import RequestLog
from app.modules.market.repositories.request_log import RequestLogRepository
from app.modules.market.scheduler_system import SYSTEM_SCHEDULES, SystemScheduleSource
from app.modules.market.services.provider import MAX_LOG_ENTRIES, REQUEST_LOG_RETENTION_DAYS
from app.modules.market.tasks import cleanup_request_log


@pytest.fixture
def repo(db_session):
    return RequestLogRepository(db_session)


@pytest.fixture
async def log_factory(db_session, save):
    async def _make(count: int, *, age_hours: float = 1.0, provider: str = 'CoinGecko'):
        return [
            await save(
                RequestLog(
                    provider_name=provider,
                    endpoint=f'v3/endpoint/{i}',
                    method='GET',
                    status_code=200,
                    response_time=0.1,
                    was_successful=True,
                    request_url=f'https://api.test/{i}',
                    created_at=datetime.now(UTC) - timedelta(hours=age_hours),
                )
            )
            for i in range(count)
        ]

    return _make


class TestGetAllByProvider:
    async def test_filters_by_provider(self, repo, log_factory):
        await log_factory(3, provider='CoinGecko')
        await log_factory(2, provider='Polygon')

        result = await repo.get_all_by_provider('Polygon', datetime.now(UTC) - timedelta(days=1))

        assert len(result) == 2
        assert all(r.provider_name == 'Polygon' for r in result)

    async def test_respects_window(self, repo, log_factory):
        await log_factory(2, age_hours=1)
        await log_factory(3, age_hours=48)

        result = await repo.get_all_by_provider('CoinGecko', datetime.now(UTC) - timedelta(hours=24))

        assert len(result) == 2

    async def test_caps_result_size(self, repo, log_factory):
        # Без предела запрос отдавал весь request_log за окно вместе с текстом
        # ответов провайдера.
        await log_factory(MAX_LOG_ENTRIES + 50)

        result = await repo.get_all_by_provider('CoinGecko', datetime.now(UTC) - timedelta(days=1))

        assert len(result) == MAX_LOG_ENTRIES

    async def test_newest_first(self, repo, log_factory):
        await log_factory(3, age_hours=1)

        result = await repo.get_all_by_provider('CoinGecko', datetime.now(UTC) - timedelta(days=1))

        times = [r.created_at for r in result]
        assert times == sorted(times, reverse=True)


class TestDeleteOlderThan:
    async def test_removes_only_old(self, repo, db_session, log_factory):
        await log_factory(2, age_hours=1)
        await log_factory(4, age_hours=24 * 60)

        removed = await repo.delete_older_than(datetime.now(UTC) - timedelta(days=30))
        await db_session.commit()

        assert removed == 4
        remaining = await repo.get_all_by_provider('CoinGecko', datetime.now(UTC) - timedelta(days=365 * 10))
        assert len(remaining) == 2

    async def test_noop_when_all_fresh(self, repo, db_session, log_factory):
        await log_factory(3, age_hours=1)

        removed = await repo.delete_older_than(datetime.now(UTC) - timedelta(days=30))
        await db_session.commit()

        assert removed == 0


class TestCleanupTask:
    # Задача открывает собственную сессию (fire-and-forget обслуживание),
    # поэтому данные должны быть закоммичены.

    async def test_removes_expired_entries(self, db_session, log_factory):
        await log_factory(5, age_hours=24 * 40)
        await db_session.commit()

        result = await cleanup_request_log(retention_days=REQUEST_LOG_RETENTION_DAYS)

        assert result['removed'] == 5

    async def test_keeps_fresh_entries(self, db_session, log_factory):
        await log_factory(2, age_hours=1)
        await log_factory(3, age_hours=24 * 40)
        await db_session.commit()

        result = await cleanup_request_log(retention_days=REQUEST_LOG_RETENTION_DAYS)

        assert result['removed'] == 3

    async def test_is_idempotent(self, db_session, log_factory):
        await log_factory(3, age_hours=24 * 40)
        await db_session.commit()

        first = await cleanup_request_log(retention_days=REQUEST_LOG_RETENTION_DAYS)
        second = await cleanup_request_log(retention_days=REQUEST_LOG_RETENTION_DAYS)

        assert first['removed'] == 3
        assert second['removed'] == 0


class TestSystemSchedule:
    async def test_source_returns_cleanup_schedule(self):
        schedules = await SystemScheduleSource().get_schedules()

        names = {s.task_name for s in schedules}
        assert 'cleanup_request_log' in names
        assert all(s.cron for s in schedules)

    def test_every_schedule_has_valid_cron(self):
        from croniter import croniter

        for schedule in SYSTEM_SCHEDULES:
            assert croniter.is_valid(schedule.cron), schedule.task_name
