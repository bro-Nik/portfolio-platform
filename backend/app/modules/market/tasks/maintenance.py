"""Фоновые задачи обслуживания: очистка unbounded-таблиц."""

from datetime import UTC, datetime, timedelta
import logging

from app.core.database import AsyncSessionLocal
from app.core.taskiq import broker
from app.modules.market.repositories.request_log import RequestLogRepository
from app.modules.market.services.provider import REQUEST_LOG_RETENTION_DAYS

logger = logging.getLogger(__name__)


@broker.task(task_name='cleanup_request_log')
async def cleanup_request_log(retention_days: int = REQUEST_LOG_RETENTION_DAYS) -> dict:
    """Удаляет записи журнала внешних запросов старше срока хранения.

    request_log пополняется каждым обращением к провайдеру и без уборки растёт
    бесконечно: это и лишний объём, и хранение текстов ответов провайдеров
    дольше, чем нужно для разбора инцидентов.
    """
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    async with AsyncSessionLocal() as session:
        removed = await RequestLogRepository(session).delete_older_than(cutoff)
        await session.commit()
    logger.info('Очищено %s записей request_log старше %s', removed, cutoff.date())
    return {'removed': removed, 'cutoff': cutoff.isoformat()}
