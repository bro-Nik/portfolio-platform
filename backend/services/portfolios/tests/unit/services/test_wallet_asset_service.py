from decimal import Decimal
from unittest.mock import patch

import pytest

from app.repositories import TransactionRepository, WalletAssetRepository
from app.services import WalletAssetService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = WalletAssetService(db_session, ctx)
    service.repo = async_mock(spec=WalletAssetRepository, session=db_session)
    service.transaction_repo = async_mock(spec=TransactionRepository, session=db_session)
    return service


class TestWalletAssetService:
    async def test_get_transactions_success(self, service, mock):
        asset_id = 1
        wallet_id = 1

        asset = mock(id=asset_id, ticker_id='USD', wallet_id=wallet_id, quantity=Decimal('10000.0'), user_id=user_id)

        transactions = [
            mock(id=1, ticker_id='USD', quantity=Decimal('5000.0'), type='Input'),
            mock(id=2, ticker_id='USD', quantity=Decimal('2000.0'), type='Output'),
        ]

        with (
            patch.object(service.repo, 'get', return_value=asset),
            patch.object(service.transaction_repo, 'get_many_by_ticker_and_wallet', return_value=transactions),
        ):
            result = await service.get_transactions(asset_id)

            assert len(result) == 2
            service.repo.get.assert_called_once_with(asset_id)
            service.transaction_repo.get_many_by_ticker_and_wallet.assert_called_once_with('USD', wallet_id)

    async def test_get_distribution_success(self, service, mock):
        asset_id = 1
        user_id = 1

        wallet1 = mock(id=1, name='Wallet 1', user_id=user_id)
        wallet2 = mock(id=2, name='Wallet 2', user_id=user_id)

        asset = mock(id=asset_id, ticker_id='USD', wallet=wallet1, quantity=Decimal('7000.0'), user_id=user_id)

        assets = [
            mock(wallet=wallet1, quantity=Decimal('7000.0'), user_id=user_id),
            mock(wallet=wallet2, quantity=Decimal('3000.0'), user_id=user_id),
        ]

        with (
            patch.object(service.repo, 'get', return_value=asset),
            patch.object(service.repo, 'get_many_by_ticker_and_user_with_wallets', return_value=assets),
        ):
            result = await service.get_distribution(asset_id)

            assert result['total_quantity_all_wallets'] == Decimal('10000.0')
            assert len(result['wallets']) == 2
            assert result['wallets'][0]['wallet_id'] == 1
            assert result['wallets'][0]['percentage_of_total'] == 70.0

            service.repo.get.assert_called_once_with(asset_id)
            service.repo.get_many_by_ticker_and_user_with_wallets.assert_called_once_with('USD', user_id)

    async def test_handle_transaction_trade_execution(self, service, mock):
        transaction = mock(
            ticker_id='BTC',
            ticker2_id='USD',
            quantity=Decimal('1.0'),
            quantity2=Decimal('50000.0'),
            type='Buy',
            order=False,
            user_id=user_id,
        )
        transaction.get_direction.return_value = 1

        asset1 = mock(ticker_id='BTC', quantity=Decimal(0), user_id=user_id)
        asset2 = mock(ticker_id='USD', quantity=Decimal(100000), user_id=user_id)

        with (
            patch.object(service.repo, 'get_or_create', side_effect=[asset1, asset2]),
        ):
            await service.handle_transaction(transaction)

        assert asset1.quantity == Decimal('1.0')  # BTC добавлено
        assert asset2.quantity == Decimal('50000.0')  # USD потрачено (10000 - 1500)

    async def test_handle_transaction_trade_order(self, service, mock):
        transaction = mock(
            ticker_id='BTC',
            ticker2_id='USD',
            quantity=Decimal('1.0'),
            quantity2=Decimal('50000.0'),
            price=Decimal('50000.0'),
            price_usd=Decimal('50000.0'),
            type='Buy',
            order=True,
            user_id=user_id,
        )
        transaction.get_direction.return_value = 1

        asset1 = mock(ticker_id='BTC', buy_orders=Decimal(0), user_id=user_id)
        asset2 = mock(ticker_id='USD', sell_orders=Decimal(0), user_id=user_id)

        with (
            patch.object(service.repo, 'get_or_create', side_effect=[asset1, asset2]),
        ):
            await service.handle_transaction(transaction)

        # Ордеры на покупку
        assert asset1.buy_orders == Decimal('50000.0')
        assert asset2.sell_orders == Decimal('-50000.0')

        # Ордеры на продажу
        transaction.type = 'Sell'

        asset3 = mock(ticker_id='BTC', sell_orders=Decimal(0), user_id=user_id)
        asset4 = mock(ticker_id='USD', sell_orders=Decimal(0), user_id=user_id)

        with (
            patch.object(service.repo, 'get_or_create', side_effect=[asset3, asset4]),
        ):
            await service.handle_transaction(transaction)

        assert asset3.sell_orders == Decimal('-1.0')

    async def test_handle_transaction_earning(self, service, mock):
        transaction = mock(ticker_id='USD', quantity=Decimal('1000.0'), type='Earning', user_id=user_id)
        transaction.get_direction.return_value = 1

        asset = mock(ticker_id='USD', quantity=Decimal(0))

        with (
            patch.object(service.repo, 'get_or_create', return_value=asset),
        ):
            await service.handle_transaction(transaction)

        assert asset.quantity == Decimal('1000.0')

    async def test_handle_transaction_transfer(self, service, mock):
        transaction = mock(quantity=Decimal('0.5'), type='TransferOut', user_id=user_id)
        transaction.get_direction.return_value = -1

        asset1 = mock(quantity=Decimal('2.0'), user_id=user_id)
        asset2 = mock(quantity=Decimal('1.0'), user_id=user_id)

        with (
            patch.object(service.repo, 'get_or_create', side_effect=[asset1, asset2]),
        ):
            await service.handle_transaction(transaction)

        assert asset1.quantity == Decimal('1.5')  # 2 - 0.5
        assert asset2.quantity == Decimal('1.5')  # 1 + 0.5

    async def test_handle_transaction_input_output(self, service, mock):
        # Ввод
        transaction = mock(quantity=Decimal('5000.0'), type='Input', user_id=user_id)
        transaction.get_direction.return_value = 1

        asset = mock(quantity=Decimal(0), user_id=user_id)

        with (
            patch.object(service.repo, 'get_or_create', return_value=asset),
        ):
            await service.handle_transaction(transaction)

        assert asset.quantity == Decimal('5000.0')

        # Вывод
        transaction.type = 'Output'
        transaction.quantity = Decimal('2000.0')
        transaction.get_direction.return_value = -1

        asset.quantity = Decimal('10000.0')

        with (
            patch.object(service.repo, 'get_or_create', return_value=asset),
        ):
            await service.handle_transaction(transaction)

        assert asset.quantity == Decimal('8000.0')  # 10000 - 2000

    async def test_handle_transaction_with_cancel(self, service, mock):
        transaction = mock(
            ticker_id='BTC',
            ticker2_id='USDT',
            quantity=Decimal('1.0'),
            quantity2=Decimal('20000.0'),
            type='Buy',
            wallet_id=1,
            order=False,
            user_id=user_id,
        )
        transaction.get_direction.return_value = -1

        asset1 = mock(ticker_id='BTC', quantity=Decimal('5.0'), user_id=user_id)
        asset2 = mock(ticker_id='USD', quantity=Decimal(100000), user_id=user_id)

        with (
            patch.object(service.repo, 'get_or_create', side_effect=[asset1, asset2]),
        ):
            await service.handle_transaction(transaction, cancel=True)

        assert asset1.quantity == Decimal('4.0')  # 5 - 1
        assert asset2.quantity == Decimal('120000.0')  # 5 - 1
