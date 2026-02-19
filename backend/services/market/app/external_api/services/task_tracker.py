from datetime import datetime, timezone
from typing import Optional

from app.repositories.sync_repo.api_task import ApiTaskRepository

from app.models import ApiTask
from app.dependencies import get_sync_db
from app.services.task_sync import get_next_run_time


class ApiTaskTracker:
    """
    Трекер для отслеживания состояния выполнения API задач.
    
    Предоставляет методы для обновления статуса задачи на различных этапах выполнения.
    """
    def get_task(self, db, task_id: int) -> Optional[ApiTask]:
        repo = ApiTaskRepository(db)
        return repo.get(task_id)

    def started(self, task_id: int) -> None:
        """Обновляет статус и статистику задачи при начале выполнения"""
        with get_sync_db() as db:
            task = self.get_task(db, task_id)
            if task:
                self.update_last_run(task)
                task.run_count += 1
                task.status = 'Работает'

    def completed(self, task_id: int):
        """Обновляет статус и статистику задачи при успешном завершении"""
        with get_sync_db() as db:
            task = self.get_task(db, task_id)
            if task:
                next_run = self.update_next_run(task)
                task.success_count += 1
                if next_run:
                    task.status = 'Ожидание следующего запуска'
                else:
                    task.status = 'Завершена'

    def error(self, task_id: int, error):
        """Обновляет статус и статистику задачи при завершении с ошибкой"""
        with get_sync_db() as db:
            task = self.get_task(db, task_id)
            if task:
                task.error_count += 1
                task.last_error = error
                task.status = 'Завершена с ошибкой'

    def update_last_run(self, task: ApiTask) -> None:
        """Обновляет время последнего запуска задачи"""
        task.last_run = datetime.now(timezone.utc)

    def update_next_run(self, task: ApiTask) -> bool:
        """
        Обновляет время следующего запуска задачи.
        
        Вычисляет время следующего запуска на основе расписания задачи,
        если задача активна и имеет расписание.
        """
        next_run = None
        if task.schedule and task.is_active:
            next_run = get_next_run_time(task.schedule)

        task.next_run = next_run
        return bool(next_run)
