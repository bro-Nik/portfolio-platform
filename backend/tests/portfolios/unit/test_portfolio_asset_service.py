from unittest.mock import patch

import pytest

from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.modules.portfolios.repositories import PortfolioAssetRepository

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = PortfolioAssetService(ctx, db_session)
    service.repo = async_mock(spec=PortfolioAssetRepository, session=db_session)
    service.transaction_repo = async_mock()
    return service


class TestPortfolioAssetService:
    async def test_handle_transaction_buy_calls_get_or_create(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', ticker2_id='USDT',
            quantity=2.0, price=100.0, price_usd=100.0, type='Buy',
            user_id=user_id, order=False,
        )
        asset_btc = mock(quantity=1.0, amount=50.0, total_invested=50.0, realized_profit=0.0)
        asset_usdt = mock(quantity=0.0, amount=0.0, total_invested=0.0, realized_profit=0.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset_btc, asset_usdt)),
            patch.object(service, '_handle_trade_execution'),
        ):
            await service.handle_transaction(transaction)

            service._get_or_create.assert_called_once_with(
                (transaction.portfolio_id, transaction.ticker_id),
                (transaction.portfolio_id, transaction.ticker2_id),
            )

    async def test_handle_transaction_sell_calls_get_or_create(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', ticker2_id='USDT',
            quantity=1.0, price=200.0, price_usd=200.0, type='Sell',
            user_id=user_id, order=False,
        )
        asset_btc = mock(quantity=3.0, amount=600.0, total_invested=450.0, realized_profit=0.0)
        asset_usdt = mock(quantity=0.0, amount=0.0, total_invested=0.0, realized_profit=0.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset_btc, asset_usdt)),
            patch.object(service, '_handle_trade_execution'),
        ):
            await service.handle_transaction(transaction)

            service._get_or_create.assert_called_once()

    async def test_handle_transaction_earning(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', type='Earning', user_id=user_id,
        )
        asset = mock(quantity=1.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction)

            service._get_or_create.assert_called_once_with(
                (transaction.portfolio_id, transaction.ticker_id),
            )

    async def test_get_success(self, service, mock):
        asset = mock(id=1, user_id=user_id)
        with patch.object(service.repo, 'get', return_value=asset):
            result = await service.get(1)
            assert result == asset

    async def test_create_success(self, service, mock, data):
        asset_data = data(ticker_id=1, portfolio_id=1)
        with (
            patch.object(service.repo, 'get_by_ticker_and_portfolio', return_value=None),
            patch.object(service.repo, 'create', return_value=mock()),
        ):
            result = await service.create(asset_data)
            assert result is not None
