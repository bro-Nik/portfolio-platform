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

    async def test_handle_input_output_with_basis_reduces_amount_proportionally(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', quantity=1.0, type='Output', user_id=user_id,
            get_direction=lambda cancel=False: -1 if not cancel else 1,
        )
        asset = mock(quantity=2.0, amount=20000.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction)

            assert asset.quantity == 1.0
            assert asset.amount == 10000.0

    async def test_handle_input_output_without_basis_keeps_amount_zero(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', quantity=1.0, type='Output', user_id=user_id,
            get_direction=lambda cancel=False: -1 if not cancel else 1,
        )
        asset = mock(quantity=2.0, amount=0.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction)

            assert asset.quantity == 1.0
            assert asset.amount == 0.0

    async def test_handle_input_output_cancel_restores_amount(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', quantity=1.0, type='Output', user_id=user_id,
            get_direction=lambda cancel=False: -1 if not cancel else 1,
        )
        asset = mock(quantity=1.0, amount=10000.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction, cancel=True)

            assert asset.quantity == 2.0
            assert asset.amount == 20000.0

    async def test_handle_input_with_price_adds_amount(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', quantity=2.0, price_usd=100.0, type='Input',
            user_id=user_id, get_direction=lambda cancel=False: 1 if not cancel else -1,
        )
        asset = mock(quantity=0.0, amount=0.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction)

            assert asset.quantity == 2.0
            assert asset.amount == 200.0

    async def test_handle_input_cancel_restores_amount(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', quantity=2.0, price_usd=100.0, type='Input',
            user_id=user_id, get_direction=lambda cancel=False: 1 if not cancel else -1,
        )
        asset = mock(quantity=2.0, amount=200.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction, cancel=True)

            assert asset.quantity == 0.0
            assert asset.amount == 0.0

    async def test_handle_input_without_price_keeps_zero_basis(self, service, mock):
        transaction = mock(
            portfolio_id=1, ticker_id='BTC', quantity=2.0, price_usd=None, type='Input',
            user_id=user_id, get_direction=lambda cancel=False: 1 if not cancel else -1,
        )
        asset = mock(quantity=0.0, amount=0.0)

        with (
            patch.object(service, '_get_or_create', return_value=(asset,)),
        ):
            await service.handle_transaction(transaction)

            assert asset.quantity == 2.0
            assert asset.amount == 0.0

    async def test_archive_many(self, service):
        with patch.object(service.repo, 'update_all_by_ids') as update:
            await service.archive_many([1, 2, 3])
            update.assert_awaited_once_with([1, 2, 3], {'is_archived': True})

    async def test_archive_many_empty(self, service):
        with patch.object(service.repo, 'update_all_by_ids') as update:
            await service.archive_many([])
            update.assert_not_awaited()

    async def test_get_affected_single_query(self, service, mock):
        transaction = mock(portfolio_id=1, portfolio2_id=None, ticker_id=10, ticker2_id=None)
        affected = [mock()]
        with patch.object(
            service.repo, 'get_all_by_portfolio_tickers', return_value=affected,
        ) as get_all:
            result = await service.get_affected(transaction)
            get_all.assert_awaited_once_with({1: [10]})
            assert result == affected

    async def test_get_or_create_batches(self, service, mock):
        existing_btc = mock(portfolio_id=1, ticker_id=10)
        with (
            patch.object(
                service.repo, 'get_all_by_portfolio_tickers', return_value=[existing_btc],
            ) as get_all,
            patch.object(
                service.repo, 'create_all',
                return_value=[mock(portfolio_id=1, ticker_id=20)],
            ) as create_all,
            patch.object(service.session, 'flush'),
        ):
            result = await service._get_or_create((1, 10), (1, 20))

        get_all.assert_awaited_once_with({1: [10, 20]})
        create_all.assert_awaited_once_with(
            [{'portfolio_id': 1, 'ticker_id': 20, 'user_id': user_id}],
        )
        assert result[0] is existing_btc
        assert result[1].ticker_id == 20

    async def test_get_or_create_no_pairs(self, service):
        result = await service._get_or_create((None, None))
        assert result == ()

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
