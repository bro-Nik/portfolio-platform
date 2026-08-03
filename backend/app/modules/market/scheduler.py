from datetime import UTC, datetime
import logging

from croniter import croniter
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from taskiq import ScheduledTask, ScheduleSource

from app.core.database import AsyncSessionLocal
from app.modules.market.enums import TaskStatus
from app.modules.market.models import Task
from app.modules.market.repositories import ProviderRepository, TaskRepository

logger = logging.getLogger(__name__)


class DBScheduleSource(ScheduleSource):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
        redis: Redis | None = None,
    ) -> None:
        self._session_factory = session_factory or AsyncSessionLocal
        self._redis: Redis | None = redis

    async def get_schedules(self) -> list[ScheduledTask]:
        logger.info('Проверка БД на наличие запланированных задач...')
        async with self._session_factory() as session:
            tasks = await TaskRepository(session).get_all_active()
            active_providers = {p.name for p in await ProviderRepository(session).get_all_active()}
        logger.info('Обнаружено %s активных задач в БД', len(tasks))

        await self._recover_stale(tasks)

        now = datetime.now(UTC)
        schedules = []
        running_count = 0
        skipped_count = 0
        overdue_count = 0

        for task in tasks:
            if task.status == TaskStatus.RUNNING.value:
                running_count += 1
                continue
            if task.provider_name not in active_providers:
                skipped_count += 1
                continue
            is_overdue = task.next_run is not None and task.next_run <= now
            if is_overdue:
                overdue_count += 1
            st = self._create_scheduled_task(task, force_run=is_overdue)
            if st:
                schedules.append(st)

        if running_count:
            logger.debug('Пропущено %s выполняющихся задач', running_count)
        if skipped_count:
            logger.warning('Пропущено %s задач с неактивными провайдерами', skipped_count)
        if overdue_count:
            logger.warning('Обнаружено %s просроченных задач — запуск немедленно', overdue_count)

        logger.info('Загружено %s задач в планировщик', len(schedules))
        return schedules

    async def _recover_stale(self, tasks: list[Task]) -> None:
        redis = await self._get_redis()
        if redis is None:
            return

        running = [t for t in tasks if t.status == TaskStatus.RUNNING.value]
        if not running:
            return
        locks = await redis.mget([f'task:run:{t.id}' for t in running])
        stale = [t for t, lock in zip(running, locks, strict=True) if not lock]
        if not stale:
            return
        async with self._session_factory() as session:
            repo = TaskRepository(session)
            db_tasks = await repo.get_all_by_ids([t.id for t in stale])
            db_by_id = {db.id: db for db in db_tasks}
            for t in stale:
                db_task = db_by_id.get(t.id)
                if db_task and db_task.status == TaskStatus.RUNNING.value:
                    db_task.status = TaskStatus.FAILED.value
                    db_task.last_error = 'Stale: worker crashed?'
                    t.status = TaskStatus.FAILED.value
                    logger.warning('Сброшен stale статус задачи %s', t.id)
            await session.commit()

    async def _get_redis(self) -> Redis | None:
        if self._redis is None:
            try:
                from app.common.redis import get_redis

                self._redis = get_redis()
            except Exception:
                logger.exception('Не удалось подключиться к Redis')
                return None
        return self._redis

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
                args=[],
                kwargs={
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
