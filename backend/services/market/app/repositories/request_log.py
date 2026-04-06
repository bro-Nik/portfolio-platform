from datetime import datetime

from sqlalchemy import Integer, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RequestLog
from app.repositories import BaseRepository
from app.schemas import RequestLogCreate, RequestLogUpdate


class RequestLogRepository(BaseRepository[RequestLog, RequestLogCreate, RequestLogUpdate]):
    """Репозиторий для работы с логами API запросов."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RequestLog, session)

    async def get_stats_by_provider(self, provider_id: int, last_time: datetime) -> RequestLog:
        """Получить статистику по провайдеру."""
        query = select(
            func.count(RequestLog.id).label('total'),
            func.sum(func.cast(RequestLog.was_successful, Integer)).label('successful'),
            func.avg(RequestLog.response_time).label('avg_response_time'),
        ).where(
            RequestLog.provider_id == provider_id,
            RequestLog.created_at >= last_time,
        )

        result = await self.session.execute(query)
        return result.first()

    async def get_many_by_provider(self, provider_id: int, last_time: datetime) -> list[RequestLog]:
        """Получить логи по провайдеру."""
        return await self.get_all(
            RequestLog.provider_id == provider_id,
            RequestLog.created_at >= last_time,
            order=[desc(RequestLog.created_at)],
            relations=['provider'],
        )
