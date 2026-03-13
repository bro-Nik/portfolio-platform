from sqlalchemy.orm import Session

from app.models import Task
from app.repositories import BaseSyncRepository
from app.schemas import TaskCreate, TaskUpdate


class SyncTaskRepository(BaseSyncRepository[Task, TaskCreate, TaskUpdate]):
    """Репозиторий для работы с API задачами."""

    def __init__(self, session: Session) -> None:
        super().__init__(Task, session)

    def get_all_with_providers(self, *, only_active: bool = False) -> list[Task]:
        """Получить все задачи с провайдерами."""
        where = Task.is_active if only_active else None
        return self.get_all(where, relations=['provider'])

    def get_with_provider(self, id: int) -> Task:
        """Получить задачу с провайдером."""
        return self.get(id, relations=['provider'])
