from datetime import UTC, datetime, timedelta
from decimal import Decimal

from fastapi import status
import pytest

from app.modules.market.models import Ticker


class TestTransactionsAPI:
    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_buy_crypto(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'ticker2Id': 2,
            'quantity': '0.1',
            'quantity2': '6000.0',
            'price': '60000.0',
            'priceUsd': '59500.0',
            'type': 'Buy',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
            'comment': 'Покупка BTC',
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        assert data['success'] is True
        assert data['portfolioAssets'] is not None
        assert len(data['portfolioAssets']) > 0

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        btc = next((a for a in data_portfolio['assets'] if a['tickerId'] == 1), {})
        usdt = next((a for a in data_portfolio['assets'] if a['tickerId'] == 2), {})
        assert Decimal(btc['quantity']) == Decimal('0.1')
        assert Decimal(usdt['quantity']) == Decimal('-6000.0')

        data_wallet = (await client.get(f'/api/wallets/{wallet.id}', headers=auth_headers)).json()
        btc = next((a for a in data_wallet['assets'] if a['tickerId'] == 1), {})
        usdt = next((a for a in data_wallet['assets'] if a['tickerId'] == 2), {})
        assert Decimal(btc['quantity']) == Decimal('0.1')
        assert Decimal(usdt['quantity']) == Decimal('-6000.0')

    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_sell_crypto(self, client, auth_headers, portfolio, wallet, portfolio_asset):
        sell_transaction = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 3,
            'ticker2Id': 2,
            'quantity': '2.5',
            'quantity2': '7500.0',
            'price': '3000.0',
            'priceUsd': '2990.0',
            'type': 'Sell',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
            'comment': 'Продажа части позиции',
        }

        response = await client.post('/api/transactions/', json=sell_transaction, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        eth = next((a for a in data_portfolio['assets'] if a['tickerId'] == 3), {})
        usdt = next((a for a in data_portfolio['assets'] if a['tickerId'] == 2), {})
        assert Decimal(eth['quantity']) == Decimal('-2.5')
        assert Decimal(usdt['quantity']) == Decimal('7500.0')

        data_wallet = (await client.get(f'/api/wallets/{wallet.id}', headers=auth_headers)).json()
        eth = next((a for a in data_wallet['assets'] if a['tickerId'] == 3), {})
        usdt = next((a for a in data_wallet['assets'] if a['tickerId'] == 2), {})
        assert Decimal(eth['quantity']) == Decimal('-2.5')
        assert Decimal(usdt['quantity']) == Decimal('7500.0')

    @pytest.mark.usefixtures('tickers')
    async def test_update_transaction(self, client, auth_headers, portfolio, wallet, transaction):
        update_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'ticker2Id': 2,
            'quantity': '2.0',
            'quantity2': '20000.0',
            'price': '15000.0',
            'type': 'Buy',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }

        response = await client.put(f'/api/transactions/{transaction.id}', json=update_data, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data['success'] is True
        assert Decimal(data['transaction']['quantity']) == Decimal('2.0')

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        assets = data_portfolio['assets']
        assert len(assets) == 2
        btc = next((a for a in data_portfolio['assets'] if a['tickerId'] == 1), {})
        assert Decimal(btc['quantity']) == Decimal('0.5')

    async def test_delete_transaction(self, client, auth_headers, portfolio, wallet, transaction):
        response = await client.delete(f'/api/transactions/{transaction.id}', headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        assets = data_portfolio['assets']

        if len(assets) > 0:
            assert Decimal(assets[0]['quantity']) == Decimal('-1.5')

    @pytest.mark.usefixtures('tickers')
    async def test_output_reduces_cost_basis_proportionally(self, client, auth_headers, portfolio, wallet):
        buy = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'ticker2Id': 2,
            'quantity': '2.0',
            'quantity2': '40000.0',
            'price': '20000.0',
            'priceUsd': '20000.0',
            'type': 'Buy',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }
        response = await client.post('/api/transactions/', json=buy, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

        output = {
            'date': (datetime.now(UTC) + timedelta(minutes=1)).isoformat(),
            'tickerId': 1,
            'quantity': '1.0',
            'type': 'Output',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }
        response = await client.post('/api/transactions/', json=output, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

        sell = {
            'date': (datetime.now(UTC) + timedelta(minutes=2)).isoformat(),
            'tickerId': 1,
            'ticker2Id': 2,
            'quantity': '1.0',
            'quantity2': '25000.0',
            'price': '25000.0',
            'priceUsd': '25000.0',
            'type': 'Sell',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }
        response = await client.post('/api/transactions/', json=sell, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        btc = next(a for a in data_portfolio['assets'] if a['tickerId'] == 1)
        assert Decimal(btc['quantity']) == Decimal(0)
        assert Decimal(btc['amount']) == Decimal(0)
        assert Decimal(btc['realizedProfit']) == Decimal('5000.0')

    @pytest.mark.usefixtures('tickers')
    async def test_trade_transactions_visible_on_quote_portfolio_asset(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'ticker2Id': 2,
            'quantity': '0.1',
            'quantity2': '6000.0',
            'price': '60000.0',
            'priceUsd': '59500.0',
            'type': 'Buy',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }
        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

        data_portfolio = (await client.get(f'/api/portfolios/{portfolio.id}', headers=auth_headers)).json()
        usdt = next(a for a in data_portfolio['assets'] if a['tickerId'] == 2)

        data_asset = (
            await client.get(f'/api/portfolios/{portfolio.id}/assets/{usdt["id"]}/transactions', headers=auth_headers)
        ).json()
        assert len(data_asset) == 1
        assert data_asset[0]['type'] == 'Buy'
        assert data_asset[0]['tickerId'] == 1

    @pytest.mark.usefixtures('tickers')
    async def test_trade_transactions_visible_on_quote_wallet_asset(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'ticker2Id': 2,
            'quantity': '0.1',
            'quantity2': '6000.0',
            'price': '60000.0',
            'priceUsd': '59500.0',
            'type': 'Buy',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }
        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

        data_wallet = (await client.get(f'/api/wallets/{wallet.id}', headers=auth_headers)).json()
        usdt = next(a for a in data_wallet['assets'] if a['tickerId'] == 2)

        data_asset = (
            await client.get(f'/api/wallets/{wallet.id}/assets/{usdt["id"]}/transactions', headers=auth_headers)
        ).json()
        assert len(data_asset) == 1
        assert data_asset[0]['type'] == 'Buy'
        assert data_asset[0]['tickerId'] == 1

    @pytest.mark.usefixtures('tickers')
    async def test_transfer_visible_on_destination_portfolio_asset(self, client, auth_headers, portfolio):
        portfolio2 = (
            await client.post(
                '/api/portfolios/',
                json={'name': 'Портфель 2', 'market': 'crypto'},
                headers=auth_headers,
            )
        ).json()
        transfer_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'quantity': '1.0',
            'type': 'TransferOut',
            'portfolioId': portfolio.id,
            'portfolio2Id': portfolio2['id'],
        }
        response = await client.post('/api/transactions/', json=transfer_data, headers=auth_headers)
        assert response.status_code == status.HTTP_201_CREATED

        data_portfolio2 = (await client.get(f'/api/portfolios/{portfolio2["id"]}', headers=auth_headers)).json()
        btc = next(a for a in data_portfolio2['assets'] if a['tickerId'] == 1)

        data_asset = (
            await client.get(
                f'/api/portfolios/{portfolio2["id"]}/assets/{btc["id"]}/transactions', headers=auth_headers
            )
        ).json()
        assert len(data_asset) == 1
        assert data_asset[0]['type'] == 'TransferOut'
        assert data_asset[0]['portfolio2Id'] == portfolio2['id']

    @pytest.mark.usefixtures('tickers')
    async def test_transfer_rejects_mismatched_market(self, client, auth_headers, portfolio):
        portfolio2 = (
            await client.post(
                '/api/portfolios/',
                json={'name': 'Портфель акций', 'market': 'stocks'},
                headers=auth_headers,
            )
        ).json()
        transfer_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'quantity': '1.0',
            'type': 'TransferOut',
            'portfolioId': portfolio.id,
            'portfolio2Id': portfolio2['id'],
        }
        response = await client.post('/api/transactions/', json=transfer_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'crypto' in response.json()['detail']
        assert 'stocks' in response.json()['detail']

    @pytest.mark.usefixtures('tickers')
    async def test_transfer_allows_currency_to_any_market(self, client, auth_headers, portfolio, save, db_session):
        await save(
            db_session,
            Ticker(id=100, name='US Dollar', symbol='USD', market='currency'),
        )
        portfolio2 = (
            await client.post(
                '/api/portfolios/',
                json={'name': 'Портфель акций', 'market': 'stocks'},
                headers=auth_headers,
            )
        ).json()
        transfer_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 100,
            'quantity': '100.0',
            'type': 'TransferOut',
            'portfolioId': portfolio.id,
            'portfolio2Id': portfolio2['id'],
        }
        response = await client.post('/api/transactions/', json=transfer_data, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED

    async def test_create_transaction_invalid_type(self, client, auth_headers, portfolio):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'quantity': '10.0',
            'type': 'InvalidType',
            'portfolioId': portfolio.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_create_transaction_missing_required_fields(self, client, auth_headers):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'quantity': '10.0',
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_negative_quantity(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'ticker2Id': 2,
            'quantity': '-5.0',
            'quantity2': '50000.0',
            'price': '10000.0',
            'type': 'Buy',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'больше нуля' in response.json()['detail']

    async def test_create_transaction_unknown_ticker(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 999,
            'ticker2Id': 2,
            'quantity': '1.0',
            'quantity2': '10000.0',
            'price': '10000.0',
            'type': 'Buy',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Тикер не найден' in response.json()['detail']

    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_missing_price_for_buy(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'ticker2Id': 2,
            'quantity': '1.0',
            'quantity2': '10000.0',
            'type': 'Buy',
            'portfolioId': portfolio.id,
            'walletId': wallet.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'price' in response.json()['detail']

    @pytest.mark.usefixtures('tickers')
    async def test_create_transaction_mixed_transfer(self, client, auth_headers, portfolio, wallet):
        transaction_data = {
            'date': datetime.now(UTC).isoformat(),
            'tickerId': 1,
            'quantity': '1.0',
            'type': 'TransferOut',
            'portfolioId': portfolio.id,
            'portfolio2Id': portfolio.id,
            'wallet2Id': wallet.id,
        }

        response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'двумя портфелями или двумя кошельками' in response.json()['detail']
