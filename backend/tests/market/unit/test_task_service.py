import pytest

from app.common.exceptions import BusinessRuleError
from app.modules.market.repositories import ProviderRepository, TaskRepository
from app.modules.market.schemas.task import TaskCreateRequest, TaskUpdateRequest
from app.modules.market.services.task import TaskService


def make_service(db_session, async_mock):
    return TaskService(
        session=db_session,
        task_repo=async_mock(spec=TaskRepository, session=db_session),
        provider_repo=async_mock(spec=ProviderRepository, session=db_session),
    )


def make_active_provider(async_mock):
    provider = async_mock()
    provider.is_active = True
    return provider


class TestTaskTypeValidation:
    async def test_create_with_registered_method(self, db_session, async_mock, mock):
        service = make_service(db_session, async_mock)
        service.provider_repo.get_by_name.return_value = make_active_provider(async_mock)
        service.repo.exists_by_name.return_value = False
        created = mock(id=1)
        service.repo.create.return_value = created

        data = TaskCreateRequest(
            name='Load tickers (Coingecko)',
            provider_name='CoinGecko',
            task_type='load_tickers',
            schedule='0 0 1 * *',
        )

        result = await service.create(data)

        assert result is created
        service.repo.create.assert_awaited_once()

    async def test_create_with_unknown_method_rejected(self, db_session, async_mock):
        service = make_service(db_session, async_mock)
        service.provider_repo.get_by_name.return_value = make_active_provider(async_mock)
        service.repo.exists_by_name.return_value = False

        data = TaskCreateRequest(
            name='Bad task',
            provider_name='CoinGecko',
            task_type='nonsense',
            schedule='0 0 1 * *',
        )

        with pytest.raises(BusinessRuleError, match='не зарегистрирован'):
            await service.create(data)
        service.repo.create.assert_not_awaited()

    async def test_update_with_unknown_method_rejected(self, db_session, async_mock, mock):
        service = make_service(db_session, async_mock)
        existing = mock(id=1, name='Task', provider_name='CoinGecko', task_type='load_tickers')
        service.repo.get.return_value = existing

        data = TaskUpdateRequest(
            name='Task',
            provider_name='CoinGecko',
            task_type='nonsense',
            schedule='0 0 1 * *',
        )

        with pytest.raises(BusinessRuleError, match='не зарегистрирован'):
            await service.update(1, data)
        service.repo.update.assert_not_awaited()

    async def test_update_keeps_registered_method(self, db_session, async_mock, mock):
        service = make_service(db_session, async_mock)
        existing = mock(id=1, name='Task', provider_name='CoinGecko', task_type='load_tickers')
        service.repo.get.return_value = existing
        updated = mock(id=1)
        service.repo.update.return_value = updated

        data = TaskUpdateRequest(
            name='Task',
            provider_name='CoinGecko',
            task_type='load_tickers',
            schedule='0 0 1 * *',
        )

        result = await service.update(1, data)

        assert result is updated
        service.repo.update.assert_awaited_once()
