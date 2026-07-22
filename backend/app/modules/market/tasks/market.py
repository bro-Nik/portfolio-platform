import logging

from dishka.integrations.taskiq import inject

from app.modules.market.taskiq_setup import broker
from app.modules.market.external_api import handle_task_errors
from app.modules.market.dependencies.di import (
    ProviderFactoryDep,
    SessionDep,
    TaskTrackerServiceDep,
)

logger = logging.getLogger(__name__)


@broker.task(task_name='update_market_data')
@inject
@handle_task_errors()
async def update_market_data(
    tracker: TaskTrackerServiceDep,
    provider_factory: ProviderFactoryDep,
    session: SessionDep,
    provider_name: str,
    method: str,
    db_task_id: int,
    **kwargs,
) -> dict:
    logger.info('Запуск задачи %s: %s.%s', db_task_id, provider_name, method)
    provider = await provider_factory(provider_name, db_task_id)
    async with tracker.task_context(db_task_id):
        return await provider.execute(method, session=session, provider_name=provider_name, **kwargs)
