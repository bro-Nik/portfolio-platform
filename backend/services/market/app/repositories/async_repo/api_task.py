from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from sqlalchemy.orm import joinedload

from app import models, schemas
from .base import BaseRepository


class ApiTaskRepository(
    BaseRepository[models.ApiTask, schemas.ApiTaskCreate, schemas.ApiTaskUpdate]
):
    def __init__(self, db: AsyncSession):
        super().__init__(models.ApiTask, db)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[models.ApiTask]:
        query = (
            select(models.ApiTask)
            .options(joinedload(models.ApiTask.api_provider))
            .offset(skip)
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()
