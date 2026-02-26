from typing import List, Optional
from datetime import datetime
from shared.repositories import BaseAsyncRepository as BaseRepository

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, Integer, desc

from app import models, schemas


class ApiProviderRepository(
    BaseRepository[models.ApiProvider, schemas.ApiProviderCreate, schemas.ApiProviderUpdate]
):
    def __init__(self, db: AsyncSession):
        super().__init__(models.ApiProvider, db)

    async def get_all(
        self,
        skip: int = 0,
        limit: Optional[int] = None,
        active_only: bool = False
    ) -> List[models.ApiProvider]:
        if active_only:
            return await self.get_many_by(self.model.is_active == True, skip=skip, limit=limit)

        return await self.get_many_by(skip=skip, limit=limit)

    async def get_by_name(self, name: str) -> Optional[models.ApiProvider]:
        return await self.get_by(self.model.name == name)

    async def get_logs_to_stats(self, provider_id: int, last_time: datetime):
        """Получить статистику по провайдеру"""
        query = select(
            func.count(models.ApiRequestLog.id).label('total'),
            func.sum(func.cast(models.ApiRequestLog.was_successful, Integer)).label('successful'),
            func.avg(models.ApiRequestLog.response_time).label('avg_response_time')
        ).where(
            models.ApiRequestLog.api_provider_id == provider_id,
            models.ApiRequestLog.created_at >= last_time
        )

        result = await self.session.execute(query)
        return result.first()

    async def get_logs(self, provider_id: int, last_time: datetime, limit: int = 100):
        """Получить логи по сервису"""
        query = select(models.ApiRequestLog).where(
            models.ApiRequestLog.api_provider_id == provider_id,
            models.ApiRequestLog.created_at >= last_time
        ).order_by(desc(models.ApiRequestLog.created_at))

        if limit:
            query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()
