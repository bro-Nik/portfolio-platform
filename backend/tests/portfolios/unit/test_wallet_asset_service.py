from decimal import Decimal
from unittest.mock import patch

import pytest

from app.modules.portfolios.services.wallet_asset import WalletAssetService
from app.modules.portfolios.repositories import WalletAssetRepository

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = WalletAssetService(ctx, db_session)
    service.repo = async_mock(spec=WalletAssetRepository, session=db_session)
    service.transaction_repo = async_mock()
    return service


class TestWalletAssetService:
    async def test_handle_transaction_buy_calls_get_or_create(self, service, mock):
        transaction = mock(
            wallet_id=1, ticker_id='BTC', ticker2_id='USDT',
            quantity=Decimal('2.0'), type='Buy', user_id=user_id, order=False,
        )
        asset_btc = mock(quantity=Decimal('1.0'))
        asset_usdt = mock(quantity=Decimal('0.0'))

        with (
            patch.object(service, '_get_or_create', return_value=(asset_btc, asset_usdt)),
            patch.object(service, '_handle_trade_execution'),
        ):
            await service.handle_transaction(transaction)

            service._get_or_create.assert_called_once_with(
                (transaction.wallet_id, transaction.ticker_id),
                (transaction.wallet_id, transaction.ticker2_id),
            )

    async def test_handle_transaction_sell_calls_get_or_create(self, service, mock):
        transaction = mock(
            wallet_id=1, ticker_id='BTC', ticker2_id='USDT',
            quantity=Decimal('1.0'), type='Sell', user_id=user_id, order=False,
        )
        asset_btc = mock(quantity=Decimal('3.0'))
        asset_usdt = mock(quantity=Decimal('0.0'))

        with (
            patch.object(service, '_get_or_create', return_value=(asset_btc, asset_usdt)),
            patch.object(service, '_handle_trade_execution'),
        ):
            await service.handle_transaction(transaction)

            service._get_or_create.assert_called_once()

    async def test_handle_earning_calls_get_or_create(self, service, mock):
        transaction = mock(
            wallet_id=1, ticker_id='BTC',
            quantity=Decimal('0.1'), type='Earning', user_id=user_id,
        )
        asset = mock(quantity=Decimal('2.0'))

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction)

            service._get_or_create.assert_called_once_with(
                (transaction.wallet_id, transaction.ticker_id),
            )

    async def test_handle_input_calls_get_or_create(self, service, mock):
        transaction = mock(
            wallet_id=1, ticker_id='USDT',
            quantity=Decimal('500.0'), type='Input', user_id=user_id,
        )
        asset = mock(quantity=Decimal('1000.0'))

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction)

            service._get_or_create.assert_called_once_with(
                (transaction.wallet_id, transaction.ticker_id),
            )
