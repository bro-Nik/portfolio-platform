from datetime import UTC, datetime

from croniter import croniter
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.common.lock import RedisTaskLock
from app.core.database import AsyncSessionLocal
from app.modules.market.enums import LastRunStatus, TaskStatus
from app.modules.market.models import Task
from app.modules.market.repositories import TaskRepository


class TaskTrackerService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession], redis: Redis | None = None) -> None:
        self.session_factory = session_factory
        self.redis = redis

    def task_context(self, task_id: int):
        return _TaskContextManager(self, task_id)

    async def _acquire_lock(self, task_id: int) -> RedisTaskLock | None:
        if not self.redis:
            return None
        lock = RedisTaskLock(self.redis, f'task:run:{task_id}')
        await lock.__aenter__()
        return lock


class _TaskContextManager:
    def __init__(self, outer: TaskTrackerService, task_id: int):
        self.outer = outer
        self.task_id = task_id
        self._lock: RedisTaskLock | None = None

    async def __aenter__(self):
        self._lock = await self.outer._acquire_lock(self.task_id)
        await self._mark_started(self.task_id)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self._mark_failed(self.task_id, str(exc_val))
            else:
                await self._mark_completed(self.task_id)
        finally:
            if self._lock:
                await self._lock.__aexit__(exc_type, exc_val, exc_tb)
        return False

    async def _mark_started(self, task_id: int) -> None:
        async with AsyncSessionLocal() as session:
            task = await self._get_task(task_id, session)
            task.last_run = datetime.now(UTC)
            task.run_count += 1
            task.last_run_status = LastRunStatus.RUNNING.value
            task.status = TaskStatus.RUNNING.value
            await session.commit()

    async def _mark_completed(self, task_id: int) -> None:
        async with AsyncSessionLocal() as session:
            task = await self._get_task(task_id, session)
            task.success_count += 1
            task.last_run_status = LastRunStatus.SUCCESS.value
            next_run = self._update_next_run(task)
            task.status = TaskStatus.AWAITING_NEXT_RUN.value if next_run else TaskStatus.COMPLETED.value
            await session.commit()

    async def _mark_failed(self, task_id: int, error: str) -> None:
        async with AsyncSessionLocal() as session:
            task = await self._get_task(task_id, session)
            task.error_count += 1
            task.last_run_status = LastRunStatus.ERROR.value
            task.last_error = error
            task.status = TaskStatus.FAILED.value
            await session.commit()

    async def _get_task(self, id: int, session: AsyncSession) -> Task:
        repo = TaskRepository(session)
        task = await repo.get(id)
        if not task:
            raise ValueError(f'Task {id} not found')
        return task

    def _update_next_run(self, task: Task) -> bool:
        next_run = None
        if task.schedule and task.is_active:
            try:
                cron = croniter(task.schedule, datetime.now(UTC))
                next_run = cron.get_next(datetime)
            except Exception:
                pass
        task.next_run = next_run
        return next_run is not None
