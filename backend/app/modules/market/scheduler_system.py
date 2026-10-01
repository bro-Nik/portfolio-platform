"""Фоновое обслуживание, не привязанное к провайдерам.

Расписание таких задач задаётся кодом, а не строкой в таблице task: они не
принадлежат API-провайдеру, не имеют его методов и не должны появляться в
админском интерфейсе как «задачи рынка».
"""

from collections.abc import AsyncIterator
import logging

from taskiq import ScheduledTask
from taskiq.abc.schedule_source import ScheduleSource

from app.modules.market.services.provider import REQUEST_LOG_RETENTION_DAYS

logger = logging.getLogger(__name__)


SYSTEM_SCHEDULES: tuple[ScheduledTask, ...] = (
    ScheduledTask(
        task_name='cleanup_request_log',
        cron='30 4 * * *',
        args=(),
        kwargs={'retention_days': REQUEST_LOG_RETENTION_DAYS},
        labels={'source': 'system'},
    ),
    ScheduledTask(
        # Истёкший refresh-токен тянет за собой сессию с её IP и отпечатком
        # устройства, поэтому чистим его ежечасно, а не раз в сутки.
        task_name='cleanup_expired_tokens',
        cron='17 * * * *',
        args=(),
        kwargs={},
        labels={'source': 'system'},
    ),
)


class SystemScheduleSource(ScheduleSource):
    """Источник расписаний, определённых в коде."""

    async def get_schedules(self) -> list[ScheduledTask]:
        return list(SYSTEM_SCHEDULES)

    async def shutdown(self) -> None:
        return None


async def iter_system_schedules() -> AsyncIterator[ScheduledTask]:
    for schedule in SYSTEM_SCHEDULES:
        yield schedule
