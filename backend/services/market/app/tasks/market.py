import logging

from dishka.integrations.taskiq import inject

from app.core.taskiq import broker
from app.dependencies.di import ProviderFactoryDep, TaskTrackerServiceDep
from app.external_api import handle_task_errors

logger = logging.getLogger(__name__)


@broker.task(task_name='update_market_data')
@handle_task_errors()
@inject
async def update_market_data(
    tracker: TaskTrackerServiceDep,
    provider_factory: ProviderFactoryDep,
    provider_name: str,
    method: str,
    db_task_id: int,
    **kwargs,
) -> dict:
    """Универсальная задача для работы с внешними API."""
    logger.info('Запуск задачи %s: %s.%s', db_task_id, provider_name, method)
    provider = await provider_factory(provider_name, db_task_id)

    async with tracker.task_context(db_task_id):
        return await provider.execute(method, **kwargs)
