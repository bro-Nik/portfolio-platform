from unittest.mock import patch

import pytest

from shared.exceptions import ConflictError, NotFoundError

from app.repositories import PortfolioRepository
from app.services import PortfolioAssetService, PortfolioService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = PortfolioService(db_session, ctx)
    service.repo = async_mock(spec=PortfolioRepository, session=db_session)
    service.asset_service = async_mock(spec=PortfolioAssetService, session=db_session)
    return service


class TestPortfolioService:
    async def test_get_all_with_assets_success(self, service, mock):
        portfolios = [
            mock(id=1, name='Test1', user_id=user_id),
            mock(id=2, name='Test2', user_id=user_id),
        ]

        with (
            patch.object(service.repo, 'get_all_by_user_with_assets', return_value=portfolios),
        ):
            result = await service.get_all_with_assets()

            assert len(result) == 2
            assert result[0].name == 'Test1'
            assert result[1].name == 'Test2'
            service.repo.get_all_by_user_with_assets.assert_called_once_with(user_id)

    async def test_get_with_assets_success(self, service, mock):
        portfolio = mock(id=1, name='Test', assets=[mock()], user_id=user_id)

        with (
            patch.object(service.repo, 'get_with_assets', return_value=portfolio),
        ):
            result = await service.get_with_assets(portfolio.id)

            assert result.id == portfolio.id
            assert result.name == 'Test'
            assert len(result.assets) == 1
            service.repo.get_with_assets.assert_called_once_with(portfolio.id)

    async def test_get_with_assets_not_found(self, service):
        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.get(999)

    async def test_create_success(self, service, mock, data):
        portfolio_data = data(name='New Portfolio', market='stocks')
        portfolio = mock(name='New Portfolio', user_id=user_id)

        with (
            patch.object(service.repo, 'exists_by_name_and_user', return_value=False),
            patch.object(service.repo, 'create', return_value=portfolio),
        ):
            result = await service.create(portfolio_data)

            assert result.name == 'New Portfolio'
            service.repo.exists_by_name_and_user.assert_called_once_with('New Portfolio', 1)
            service.repo.create.assert_called_once()
            service.session.flush.assert_called_once()

    async def test_create_duplicate_name(self, service, data):
        portfolio_data = data(name='Existing Portfolio')

        with (
            patch.object(service.repo, 'exists_by_name_and_user', return_value=True),
            pytest.raises(ConflictError, match='уже существует'),
        ):
            await service.create(portfolio_data)

    async def test_update_success(self, service, mock, data):
        portfolio_data = data(name='Updated Name')
        existing_portfolio = mock(id=1, name='Old Name', user_id=user_id)
        updated_portfolio = mock(id=1, name='Updated Name', user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=existing_portfolio),
            patch.object(service.repo, 'exists_by_name_and_user', return_value=False),
            patch.object(service.repo, 'update', return_value=updated_portfolio),
        ):
            result = await service.update(existing_portfolio.id, portfolio_data)

            assert result.name == 'Updated Name'
            service.repo.get.assert_called_with(existing_portfolio.id)
            service.repo.exists_by_name_and_user.assert_called_once_with('Updated Name', existing_portfolio.id)

    async def test_delete_success(self, service, mock):
        portfolio = mock(id=1, user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=portfolio),
            patch.object(service.repo, 'delete', return_value=True),
        ):
            await service.delete(portfolio.id)

            service.repo.get.assert_called_once_with(portfolio.id)
            service.repo.delete.assert_called_once_with(portfolio.id)

    async def test_add_asset_success(self, service, mock, data):
        """Тест добавления актива в портфель."""
        asset_data = data(ticker_id='AAPL')
        portfolio = mock(id=1, name='Test Portfolio', user_id=user_id)
        asset = mock(id=123)

        with (
            patch.object(service, 'get', return_value=portfolio),
            patch.object(service.asset_service, 'create', return_value=asset),
        ):
            await service.add_asset(portfolio.id, asset_data)

            service.asset_service.create.assert_called_once_with(asset_data)
            service.get.assert_called_once_with(portfolio.id)

    async def test_handle_transaction_trade_success(self, service, mock):
        transaction = mock(portfolio_id=1, type='Buy')
        portfolio = mock(id=1, user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=portfolio),
        ):
            await service.handle_transaction(transaction)

            service.repo.get.assert_called_once_with(portfolio.id)
            service.asset_service.handle_transaction.assert_called_once_with(transaction, cancel=False)

    async def test_handle_transaction_no_portfolio(self, service, mock):
        transaction = mock(portfolio_id=None, type='Buy', user_id=user_id)

        await service.handle_transaction(transaction)

        service.repo.get.assert_not_called()
        service.asset_service.handle_transaction.assert_not_called()
