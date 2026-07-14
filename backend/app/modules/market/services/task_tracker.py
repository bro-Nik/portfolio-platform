from datetime import UTC, datetime

from croniter import croniter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import AsyncSessionLocal
from app.modules.market.models import Task
from app.modules.market.repositories import TaskRepository


class TaskTrackerService:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    def task_context(self, task_id: int):
        return _TaskContextManager(self, task_id)


class _TaskContextManager:
    def __init__(self, outer: TaskTrackerService, task_id: int):
        self.outer = outer
        self.task_id = task_id

    async def __aenter__(self):
        await self._mark_started(self.task_id)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._mark_failed(self.task_id, str(exc_val))
        else:
            await self._mark_completed(self.task_id)
        return False

    async def _mark_started(self, task_id: int) -> None:
        async with AsyncSessionLocal() as session:
            task = await self._get_task(task_id, session)
            task.last_run = datetime.now(UTC)
            task.run_count += 1
            task.last_run_status = 'running'
            task.status = 'Running'
            await session.commit()

    async def _mark_completed(self, task_id: int) -> None:
        async with AsyncSessionLocal() as session:
            task = await self._get_task(task_id, session)
            task.success_count += 1
            task.last_run_status = 'success'
            next_run = self._update_next_run(task)
            task.status = 'Awaiting next run' if next_run else 'Completed'
            await session.commit()

    async def _mark_failed(self, task_id: int, error: str) -> None:
        async with AsyncSessionLocal() as session:
            task = await self._get_task(task_id, session)
            task.error_count += 1
            task.last_run_status = 'error'
            task.last_error = error
            task.status = 'Failed'
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
