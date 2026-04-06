import logging

from croniter import croniter
from taskiq import ScheduledTask, ScheduleSource

from app.core.db import SessionLocal
from app.models import Task
from app.repositories.task import TaskRepository

logger = logging.getLogger(__name__)


class DBScheduleSource(ScheduleSource):
    """Берет расписание из БД."""

    async def get_schedules(self) -> list[ScheduledTask]:
        """Загрузка запланированных задач из БД."""
        logger.info('Проверка БД на наличие запланированных задач....')

        async with SessionLocal() as session:
            tasks = await TaskRepository(session).get_all_active_with_providers()

        logger.info('Обнаружено %s активных задач в БД', len(tasks))

        schedules = [st for task in tasks if (st := self._create_scheduled_task(task))]

        logger.info('Успешно загружено %s задач в планировщик', len(schedules))
        return schedules

    def _create_scheduled_task(self, task: Task) -> ScheduledTask | None:
        try:
            if not task.provider:
                logger.warning('Задача %s не имеет провайдера - пропуск', task.id)
                return None

            if not croniter.is_valid(task.schedule):
                logger.error('Недействительный cron: %s', task.schedule)
                return None

            return ScheduledTask(
                task_name='update_market_data',
                cron=task.schedule,
                args=[],
                kwargs={
                    'provider_name': task.provider.name,
                    'method': task.task_type,
                    'db_task_id': str(task.id),
                    **task.parameters,
                },
                labels={
                    'source': 'database',
                    'task_id': str(task.id),
                    'provider': task.provider.name,
                },
            )
        except Exception:
            logger.exception('Ошибка создания задачи %s', task.id)
            return None
