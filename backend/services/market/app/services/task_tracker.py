from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from croniter import croniter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core import auto_commit_session
from app.models import Task
from app.repositories import TaskRepository


class TaskTrackerService:
    """Сервис для отслеживания выполнения фоновых задач."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    @asynccontextmanager
    async def task_context(self, task_id: int) -> AsyncIterator[None]:
        """Контекстный менеджер для отслеживания задачи.

        Автоматически:
        - Отмечает старт задачи
        - При успехе отмечает завершение
        - При ошибке отмечает ошибку
        """
        await self._mark_started(task_id)
        try:
            yield
        except Exception as e:
            await self._mark_failed(task_id, str(e))
            raise
        else:
            await self._mark_completed(task_id)

    async def _mark_started(self, task_id: int) -> None:
        async with auto_commit_session(self.session_factory) as session:
            task = await self._get_task(task_id, session)
            task.last_run = datetime.now(UTC)
            task.run_count += 1
            task.last_run_status = 'running'
            task.status = 'Работает'

    async def _mark_completed(self, task_id: int) -> None:
        async with auto_commit_session(self.session_factory) as session:
            task = await self._get_task(task_id, session)
            task.success_count += 1
            task.last_run_status = 'success'
            next_run = self._update_next_run(task)
            if next_run:
                task.status = 'Ожидание следующего запуска'
            else:
                task.status = 'Завершена'

    async def _mark_failed(self, task_id: int, error: str) -> None:
        async with auto_commit_session(self.session_factory) as session:
            task = await self._get_task(task_id, session)
            task.error_count += 1
            task.last_run_status = 'error'
            task.last_error = error
            task.status = 'Завершена с ошибкой'

    async def _get_task(self, id: int, session: AsyncSession) -> Task:
        repo = TaskRepository(session)
        task = await repo.get(id)
        if not task:
            raise ValueError(f'Задача {id} не найдена')
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
