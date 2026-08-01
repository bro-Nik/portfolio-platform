from datetime import UTC, datetime
from decimal import Decimal

from fastapi import status
import pytest


class TestTransactionsAPI:
    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_buy_crypto(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 1,
            'ticker2_id': 2,
            'quantity': '0.1',
            'quantity2': '6000.0',
            'price': '60000.0',
            'price_usd': '59500.0',
            'type': 'Buy',
            'portfolio_id': portfolio.id,
            'wallet_id': wallet.id,
            'comment': 'Покупка BTC',
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data['success'] is True
        assert data['portfolio_assets'] is not None
        assert len(data['portfolio_assets']) > 0

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        btc = next((a for a in data_portfolio['assets'] if a['ticker_id'] == 1), {})
        usdt = next((a for a in data_portfolio['assets'] if a['ticker_id'] == 2), {})
        assert Decimal(btc['quantity']) == Decimal('0.1')
        assert Decimal(usdt['quantity']) == Decimal('-6000.0')

        data_wallet = (await client.get(f'/api/wallets/{wallet.id}', headers=auth_headers)).json()
        btc = next((a for a in data_wallet['assets'] if a['ticker_id'] == 1), {})
        usdt = next((a for a in data_wallet['assets'] if a['ticker_id'] == 2), {})
        assert Decimal(btc['quantity']) == Decimal('0.1')
        assert Decimal(usdt['quantity']) == Decimal('-6000.0')

    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_sell_crypto(self, client, auth_headers, portfolio, wallet, portfolio_asset):
        sell_transaction = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 3,
            'ticker2_id': 2,
            'quantity': '2.5',
            'quantity2': '7500.0',
            'price': '3000.0',
            'price_usd': '2990.0',
            'type': 'Sell',
            'portfolio_id': portfolio.id,
            'wallet_id': wallet.id,
            'comment': 'Продажа части позиции',
        }

        response = await client.post('/api/transactions/', json=sell_transaction, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        eth = next((a for a in data_portfolio['assets'] if a['ticker_id'] == 3), {})
        usdt = next((a for a in data_portfolio['assets'] if a['ticker_id'] == 2), {})
        assert Decimal(eth['quantity']) == Decimal('-2.5')
        assert Decimal(usdt['quantity']) == Decimal('7500.0')

        data_wallet = (await client.get(f'/api/wallets/{wallet.id}', headers=auth_headers)).json()
        eth = next((a for a in data_wallet['assets'] if a['ticker_id'] == 3), {})
        usdt = next((a for a in data_wallet['assets'] if a['ticker_id'] == 2), {})
        assert Decimal(eth['quantity']) == Decimal('-2.5')
        assert Decimal(usdt['quantity']) == Decimal('7500.0')

    @pytest.mark.usefixtures('tickers')
    async def test_update_transaction(self, client, auth_headers, portfolio, wallet, transaction):
        update_data = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 1,
            'ticker2_id': 2,
            'quantity': '2.0',
            'quantity2': '20000.0',
            'price': '15000.0',
            'type': 'Buy',
            'portfolio_id': portfolio.id,
            'wallet_id': wallet.id,
        }

        response = await client.put(f'/api/transactions/{transaction.id}', json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data['success'] is True
        assert Decimal(data['transaction']['quantity']) == Decimal('2.0')

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        assets = data_portfolio['assets']
        assert len(assets) == 2
        btc = next((a for a in data_portfolio['assets'] if a['ticker_id'] == 1), {})
        assert Decimal(btc['quantity']) == Decimal('0.5')

    async def test_delete_transaction(self, client, auth_headers, portfolio, wallet, transaction):
        response = await client.delete(f'/api/transactions/{transaction.id}', headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data['success'] is True

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        assets = data_portfolio['assets']

        if len(assets) > 0:
            assert Decimal(assets[0]['quantity']) == Decimal('-1.5')

    async def test_create_transaction_invalid_type(self, client, auth_headers, portfolio):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 1,
            'quantity': '10.0',
            'type': 'InvalidType',
            'portfolio_id': portfolio.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_transaction_missing_required_fields(self, client, auth_headers):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 1,
            'quantity': '10.0',
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_negative_quantity(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 1,
            'ticker2_id': 2,
            'quantity': '-5.0',
            'quantity2': '50000.0',
            'price': '10000.0',
            'type': 'Buy',
            'portfolio_id': portfolio.id,
            'wallet_id': wallet.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'больше нуля' in response.json()['detail']

    async def test_create_transaction_unknown_ticker(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 999,
            'ticker2_id': 2,
            'quantity': '1.0',
            'quantity2': '10000.0',
            'price': '10000.0',
            'type': 'Buy',
            'portfolio_id': portfolio.id,
            'wallet_id': wallet.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Тикер не найден' in response.json()['detail']

    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_missing_price_for_buy(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 1,
            'ticker2_id': 2,
            'quantity': '1.0',
            'quantity2': '10000.0',
            'type': 'Buy',
            'portfolio_id': portfolio.id,
            'wallet_id': wallet.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'price' in response.json()['detail']

    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_mixed_transfer(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 1,
            'quantity': '1.0',
            'type': 'TransferOut',
            'portfolio_id': portfolio.id,
            'portfolio2_id': portfolio.id,
            'wallet2_id': wallet.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'двумя портфелями или двумя кошельками' in response.json()['detail']
