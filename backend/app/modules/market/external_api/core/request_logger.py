import logging
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.database import AsyncSessionLocal as session_factory
from app.modules.market.models import RequestLog

logger = logging.getLogger(__name__)
MAX_LOGS_TO_SAVE = 30


class RequestLogger:
    def __init__(self, provider_name: str, task_id: int, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.provider_name = provider_name
        self.task_id = task_id
        self._logs = []

    async def log(self, method: str, endpoint: str, response: httpx.Response | None,
                  params: dict[str, Any] | None, response_time: float, error: str | None = None) -> None:
        log = RequestLog(
            provider_name=self.provider_name, task_id=self.task_id, endpoint=endpoint,
            method=method, request_params=params or {},
            status_code=response.status_code if response else None,
            response_time=response_time,
            was_successful=response.is_success if response else False,
            error_message=error if not response else (None if response.is_success else response.text[:500] or error),
        )
        self._logs.append(log)
        if len(self._logs) > MAX_LOGS_TO_SAVE:
            await self.save()

    async def save(self) -> None:
        if self._logs:
            logs_to_save = self._logs.copy()
            self._logs = []
            async with session_factory() as session:
                session.add_all(logs_to_save)
                await session.commit()
            logger.info('Логи запросов сохранены')
