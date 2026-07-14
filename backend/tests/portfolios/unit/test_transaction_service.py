from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from app.common.exceptions import BusinessRuleError, NotFoundError

from app.modules.portfolios.repositories import TransactionRepository
from app.modules.portfolios.services.portfolio import PortfolioService
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.modules.portfolios.services.transaction import TransactionService
from app.modules.portfolios.services.wallet import WalletService
from app.modules.portfolios.services.wallet_asset import WalletAssetService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = TransactionService(db_session, ctx)
    service.repo = async_mock(spec=TransactionRepository, session=db_session)
    service.portfolio_service = async_mock(spec=PortfolioService, session=db_session)
    service.portfolio_asset_service = async_mock(spec=PortfolioAssetService, session=db_session)
    service.wallet_service = async_mock(spec=WalletService, session=db_session)
    service.wallet_asset_service = async_mock(spec=WalletAssetService, session=db_session)
    return service


class TestTransactionService:
    async def test_create_success(self, service, mock, data):
        transaction_data = data(
            date=datetime.now(UTC), type='Buy', portfolio_id=1, wallet_id=1,
            ticker_id='AAPL', ticker2_id='USD', quantity=Decimal(10),
        )
        transaction = mock(
            id=1, type='Buy', user_id=user_id,
            portfolio_id=1, wallet_id=1,
        )

        with (
            patch.object(service.repo, 'create', return_value=transaction),
        ):
            result = await service.create(transaction_data)

            service.repo.create.assert_called_once()
            service.portfolio_service.handle_transaction.assert_called_once_with(transaction, cancel=False)
            service.wallet_service.handle_transaction.assert_called_once_with(transaction, cancel=False)
            assert result == transaction

    async def test_create_invalid_type(self, service, mock):
        transaction_data = mock(
            type='InvalidType',
        )

        with pytest.raises(BusinessRuleError, match='Неизвестный тип транзакции'):
            await service.create(transaction_data)

    async def test_get_success(self, service, mock):
        transaction = mock(id=1, user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=transaction),
        ):
            result = await service.get(1)
            assert result == transaction

    async def test_get_not_found(self, service):
        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найдена'),
        ):
            await service.get(999)

    async def test_delete_success(self, service, mock):
        transaction = mock(
            id=1, portfolio_id=1, wallet_id=1, user_id=user_id, type='Buy',
        )

        with (
            patch.object(service, 'get', return_value=transaction),
            patch.object(service.repo, 'delete', return_value=True),
        ):
            result = await service.delete(transaction.id)

            service.portfolio_service.handle_transaction.assert_called_once_with(transaction, cancel=True)
            service.wallet_service.handle_transaction.assert_called_once_with(transaction, cancel=True)
            service.repo.delete.assert_called_once_with(transaction.id)
            assert result == transaction
