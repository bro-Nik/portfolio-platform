from shared.repositories import BaseSyncRepository as BaseRepository
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app import models, schemas


class ApiTaskRepository(
    BaseRepository[models.ApiTask, schemas.ApiTaskCreate, schemas.ApiTaskUpdate]
):
    def __init__(self, session: Session):
        super().__init__(models.ApiTask, session)

    def get_all_with_providers(self, only_active: bool = False):
        query = (
            select(models.ApiTask)
            .options(joinedload(models.ApiTask.api_provider))
        )
        # Только активные задачи
        if only_active:
            query = query.where(models.ApiTask.is_active == True)

        result = self.session.execute(query)
        return result.scalars().all()

    def get_with_provider(self, task_id):
        query = (
            select(models.ApiTask)
            .options(joinedload(models.ApiTask.api_provider))
            .where(models.ApiTask.id == task_id)
        )

        result = self.session.execute(query)
        return result.scalar_one_or_none()
