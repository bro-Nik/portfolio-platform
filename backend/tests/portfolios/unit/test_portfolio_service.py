from unittest.mock import patch

import pytest

from app.common.exceptions import ConflictError, NotFoundError

from app.modules.portfolios.repositories import PortfolioRepository
from app.modules.portfolios.services.portfolio import PortfolioService
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = PortfolioService(db_session, ctx, taggable_repo=async_mock())
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
            patch.object(service.taggable_repo, 'bulk_get_tags', return_value={}),
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
            patch.object(service.taggable_repo, 'bulk_get_tags', return_value={}),
        ):
            result = await service.get_with_assets(portfolio.id)

            assert result.id == portfolio.id
            assert result.name == 'Test'
            assert len(result.assets) == 1
            service.repo.get_with_assets.assert_called_once_with(portfolio.id)
            service.taggable_repo.bulk_get_tags.assert_awaited_once()

    async def test_archive_bulk(self, service, mock):
        portfolio = mock(
            id=1, user_id=user_id,
            assets=[mock(id=10, is_archived=False), mock(id=11, is_archived=True)],
        )

        with (
            patch.object(service.repo, 'get_with_assets', return_value=portfolio),
            patch.object(service.repo, 'update', return_value=portfolio),
            patch.object(service.session, 'commit'),
        ):
            await service.archive(portfolio.id)

            service.repo.get_with_assets.assert_awaited_once_with(portfolio.id)
            service.asset_service.archive_many.assert_awaited_once_with([10])
            service.asset_service.archive.assert_not_awaited()

    async def test_archive_no_unarchived_assets(self, service, mock):
        portfolio = mock(id=1, user_id=user_id, assets=[])

        with (
            patch.object(service.repo, 'get_with_assets', return_value=portfolio),
            patch.object(service.repo, 'update', return_value=portfolio),
            patch.object(service.session, 'commit'),
        ):
            await service.archive(portfolio.id)

            service.asset_service.archive_many.assert_not_awaited()

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
            service.session.commit.assert_called_once()

    async def test_create_duplicate_name(self, service, data):
        portfolio_data = data(name='Existing Portfolio')

        with (
            patch.object(service.repo, 'exists_by_name_and_user', return_value=True),
            pytest.raises(ConflictError, match='уже существует'),
        ):
            await service.create(portfolio_data)

    async def test_update_success(self, service, mock, data):
        portfolio_data = data(name='Updated Name', market=None)
        existing_portfolio = mock(id=1, name='Old Name', user_id=user_id, is_archived=False)
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
            service.repo.get_with_assets.assert_not_awaited()

    async def test_update_market_empty_success(self, service, mock, data):
        portfolio_data = data(name='Old Name', market='stocks')
        existing_portfolio = mock(id=1, name='Old Name', market='crypto', user_id=user_id, is_archived=False)
        portfolio_with_assets = mock(id=1, name='Old Name', market='crypto', assets=[], user_id=user_id)
        updated_portfolio = mock(id=1, name='Old Name', market='stocks', user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=existing_portfolio),
            patch.object(service.repo, 'get_with_assets', return_value=portfolio_with_assets),
            patch.object(service.repo, 'update', return_value=updated_portfolio),
        ):
            result = await service.update(existing_portfolio.id, portfolio_data)

            assert result.market == 'stocks'
            service.repo.get_with_assets.assert_awaited_once_with(existing_portfolio.id)
            service.repo.exists_by_name_and_user.assert_not_awaited()

    async def test_update_market_with_assets_rejected(self, service, mock, data):
        portfolio_data = data(name='Old Name', market='stocks')
        existing_portfolio = mock(id=1, name='Old Name', market='crypto', user_id=user_id, is_archived=False)
        portfolio_with_assets = mock(id=1, name='Old Name', market='crypto', assets=[mock(id=10)], user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=existing_portfolio),
            patch.object(service.repo, 'get_with_assets', return_value=portfolio_with_assets),
            pytest.raises(ConflictError, match='активами'),
        ):
            await service.update(existing_portfolio.id, portfolio_data)

            service.repo.get_with_assets.assert_awaited_once_with(existing_portfolio.id)
            service.repo.update.assert_not_awaited()

    async def test_delete_success(self, service, mock):
        portfolio = mock(id=1, user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=portfolio),
            patch.object(service.transaction_repo, 'exists_for_portfolio', return_value=False),
            patch.object(service.repo, 'delete', return_value=True),
        ):
            await service.delete(portfolio.id)

            service.repo.get.assert_called_once_with(portfolio.id)
            service.repo.delete.assert_called_once_with(portfolio.id)

    async def test_add_asset_success(self, service, mock, data):
        asset_data = data(ticker_id=1)
        portfolio = mock(id=1, name='Test Portfolio', user_id=user_id, is_archived=False)
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

        await service.handle_transaction(transaction)

        service.asset_service.handle_transaction.assert_called_once_with(transaction, cancel=False)

    async def test_handle_transaction_no_portfolio(self, service, mock):
        transaction = mock(portfolio_id=None, type='Buy', user_id=user_id)

        await service.handle_transaction(transaction)

        service.asset_service.handle_transaction.assert_not_called()
