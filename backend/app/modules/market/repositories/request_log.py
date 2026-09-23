from datetime import datetime

from sqlalchemy import Integer, delete, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository
from app.modules.market.models import RequestLog


class RequestLogRepository(BaseRepository[RequestLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(RequestLog, session)

    async def get_stats_by_provider(self, provider_name: str, last_time: datetime) -> RequestLog:
        query = select(
            func.count(RequestLog.id).label('total'),
            func.sum(func.cast(RequestLog.was_successful, Integer)).label('successful'),
            func.avg(RequestLog.response_time).label('avg_response_time'),
        ).where(
            RequestLog.provider_name == provider_name,
            RequestLog.created_at >= last_time,
        )
        result = await self._session.execute(query)
        return result.first()

    async def get_all_by_provider(
        self,
        provider_name: str,
        last_time: datetime,
        limit: int = 200,
    ) -> list[RequestLog]:
        """Последние записи провайдера.

        Таблица растёт бессрочно, поэтому выборка ограничена: без предела один
        запрос отдавал бы весь request_log за окно, вместе с текстом ответов.
        """
        return await self.get_all(
            RequestLog.provider_name == provider_name,
            RequestLog.created_at >= last_time,
            order=[desc(RequestLog.created_at)],
            limit=limit,
        )

    async def delete_older_than(self, last_time: datetime) -> int:
        """Удаляет записи старше порога (retention для журнала внешних запросов)."""
        result = await self._session.execute(
            delete(RequestLog).where(RequestLog.created_at < last_time),
        )
        return result.rowcount or 0
