import logging
from datetime import UTC, datetime

from croniter import croniter
from taskiq import ScheduledTask, ScheduleSource

from app.core.database import AsyncSessionLocal
from app.modules.market.models import Task
from app.modules.market.repositories import TaskRepository

logger = logging.getLogger(__name__)


class DBScheduleSource(ScheduleSource):
    async def get_schedules(self) -> list[ScheduledTask]:
        logger.info('Проверка БД на наличие запланированных задач...')
        async with AsyncSessionLocal() as session:
            tasks = await TaskRepository(session).get_all_active()
        logger.info('Обнаружено %s активных задач в БД', len(tasks))

        now = datetime.now(UTC)
        schedules = []
        overdue_count = 0
        for task in tasks:
            is_overdue = (
                task.next_run is not None
                and task.next_run <= now
            )
            if is_overdue:
                overdue_count += 1
            st = self._create_scheduled_task(task, force_run=is_overdue)
            if st:
                schedules.append(st)

        if overdue_count:
            logger.warning('Обнаружено %s просроченных задач — запуск немедленно', overdue_count)
        logger.info('Загружено %s задач в планировщик', len(schedules))
        return schedules

    def _create_scheduled_task(self, task: Task, force_run: bool = False) -> ScheduledTask | None:
        try:
            if not force_run and not task.schedule:
                return None
            if not force_run and not croniter.is_valid(task.schedule):
                logger.error('Недействительный cron: %s', task.schedule)
                return None
            return ScheduledTask(
                task_name='update_market_data',
                cron=None if force_run else task.schedule,
                time=datetime.now(UTC) if force_run else None,
                args=[], kwargs={
                    'provider_name': task.provider_name,
                    'method': task.task_type,
                    'db_task_id': str(task.id),
                    **task.parameters,
                },
                labels={'source': 'database', 'task_id': str(task.id), 'provider': task.provider_name},
            )
        except Exception:
            logger.exception('Ошибка создания задачи %s', task.id)
            return None
