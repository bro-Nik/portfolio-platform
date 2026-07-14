from unittest.mock import patch

import pytest

from app.common.exceptions import ConflictError, NotFoundError

from app.modules.portfolios.repositories import WalletRepository
from app.modules.portfolios.services.wallet import WalletService
from app.modules.portfolios.services.wallet_asset import WalletAssetService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = WalletService(db_session, ctx)
    service.repo = async_mock(spec=WalletRepository, session=db_session)
    service.asset_service = async_mock(spec=WalletAssetService, session=db_session)
    service.taggable_repo = async_mock()
    return service


class TestWalletService:
    async def test_get_all_with_assets_success(self, service, mock):
        wallets = [
            mock(id=1, name='Wallet 1', user_id=user_id),
            mock(id=2, name='Wallet 2', user_id=user_id),
        ]

        with (
            patch.object(service.repo, 'get_all_by_user_with_assets', return_value=wallets),
            patch.object(service.taggable_repo, 'bulk_get_tags', return_value={}),
        ):
            result = await service.get_all_with_assets()

            assert len(result) == 2
            assert result[0].name == 'Wallet 1'
            assert result[1].name == 'Wallet 2'
            service.repo.get_all_by_user_with_assets.assert_called_once_with(user_id)

    async def test_get_with_assets_success(self, service, mock):
        wallet = mock(id=1, name='Test', assets=[mock()], user_id=user_id)

        with (
            patch.object(service.repo, 'get_with_assets', return_value=wallet),
        ):
            result = await service.get_with_assets(wallet.id)

            assert result.id == wallet.id
            assert result.name == 'Test'
            assert len(result.assets) == 1
            service.repo.get_with_assets.assert_called_once_with(wallet.id)

    async def test_get_with_assets_not_found(self, service):
        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.get(999)

    async def test_create_success(self, service, mock, data):
        wallet_data = data(name='New Wallet')
        wallet = mock(name='New Wallet')

        with (
            patch.object(service.repo, 'exists_by_name_and_user', return_value=False),
            patch.object(service.repo, 'create', return_value=wallet),
        ):
            result = await service.create(wallet_data)

            assert result.name == 'New Wallet'
            service.repo.exists_by_name_and_user.assert_called_once_with('New Wallet', user_id)
            service.repo.create.assert_called_once()
            service.session.flush.assert_called_once()

    async def test_create_duplicate_name(self, service, data):
        wallet_data = data(name='Existing Wallet')

        with (
            patch.object(service.repo, 'exists_by_name_and_user', return_value=True),
            pytest.raises(ConflictError, match='уже существует'),
        ):
            await service.create(wallet_data)

    async def test_update_success(self, service, mock, data):
        wallet_data = data(name='Updated Name')
        existing_wallet = mock(id=1, name='Old Name', user_id=user_id)
        updated_wallet = mock(id=1, name='Updated Name', user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=existing_wallet),
            patch.object(service.repo, 'exists_by_name_and_user', return_value=False),
            patch.object(service.repo, 'update', return_value=updated_wallet),
        ):
            result = await service.update(existing_wallet.id, wallet_data)

            assert result.name == 'Updated Name'
            service.repo.get.assert_called_with(existing_wallet.id)
            service.repo.exists_by_name_and_user.assert_called_once_with('Updated Name', existing_wallet.id)

    async def test_delete_success(self, service, mock):
        wallet = mock(id=1, user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=wallet),
            patch.object(service.repo, 'delete', return_value=True),
        ):
            await service.delete(wallet.id)

            service.repo.get.assert_called_once_with(wallet.id)
            service.repo.delete.assert_called_once_with(wallet.id)

    async def test_handle_transaction_trade_success(self, service, mock):
        transaction = mock(wallet_id=1, type='Buy')

        await service.handle_transaction(transaction)

        service.asset_service.handle_transaction.assert_called_once_with(transaction, cancel=False)

    async def test_handle_transaction_trade_with_cancel(self, service, mock):
        transaction = mock(wallet_id=1, type='Buy')

        await service.handle_transaction(transaction, cancel=True)

        service.asset_service.handle_transaction.assert_called_once_with(transaction, cancel=True)

    async def test_handle_transaction_transfer_success(self, service, mock):
        transaction = mock(wallet_id=1, wallet2_id=2, type='TransferOut')

        await service.handle_transaction(transaction)

        service.asset_service.handle_transaction.assert_called_once_with(transaction, cancel=False)

    async def test_handle_transaction_no_wallet(self, service, mock):
        transaction = mock(wallet_id=None, type='TransferOut')

        await service.handle_transaction(transaction)

        service.asset_service.handle_transaction.assert_not_called()

    async def test_handle_transaction_earning_success(self, service, mock):
        transaction = mock(wallet_id=1, type='Earning')

        await service.handle_transaction(transaction)

        service.asset_service.handle_transaction.assert_called_once()

    async def test_handle_transaction_input_output_success(self, service, mock):
        for t_type in ['Input', 'Output']:
            transaction = mock(wallet_id=1, type=t_type)

            await service.handle_transaction(transaction)

            service.asset_service.handle_transaction.assert_called_once_with(transaction, cancel=False)
            service.asset_service.handle_transaction.reset_mock()
