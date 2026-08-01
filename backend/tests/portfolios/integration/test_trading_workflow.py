from datetime import UTC, datetime

from fastapi import status
import pytest


class TestTradingWorkflow:
    @pytest.mark.usefixtures('tickers')
    async def test_complete_trading_workflow(self, client, auth_headers):
        auth_headers = {**auth_headers, 'X-Forwarded-For': '192.168.1.10'}

        portfolio_data = {
            'name': 'Мой инвестиционный портфель',
            'market': 'stock',
            'comment': 'Портфель для торговли акциями',
        }

        portfolio_response = await client.post('/api/portfolios/', json=portfolio_data, headers=auth_headers)
        assert portfolio_response.status_code == status.HTTP_201_CREATED
        portfolio_id = portfolio_response.json()['id']

        wallet_data = {
            'name': 'Торговый кошелек USD',
            'comment': 'Основной кошелек для расчетов',
        }

        wallet_response = await client.post('/api/wallets/', json=wallet_data, headers=auth_headers)
        assert wallet_response.status_code == status.HTTP_201_CREATED
        wallet_id = wallet_response.json()['id']

        funding_transaction = {
            'date': datetime.now(UTC).isoformat(),
            'ticker_id': 7,
            'quantity': '100000.0',
            'type': 'Input',
            'portfolio_id': portfolio_id,
            'wallet_id': wallet_id,
            'comment': 'Начальное пополнение',
        }

        funding_response = await client.post('/api/transactions/', json=funding_transaction, headers=auth_headers)
        assert funding_response.status_code == status.HTTP_201_CREATED

        tickers = {'AAPL': 4, 'GOOGL': 5, 'MSFT': 6}

        for ticker_id in tickers.values():
            asset_data = {'ticker_id': ticker_id, 'portfolio_id': portfolio_id}
            response = await client.post(f'/api/portfolios/{portfolio_id}/assets', json=asset_data, headers=auth_headers)
            assert response.status_code == status.HTTP_201_CREATED

        trades = [
            {'ticker': 'AAPL', 'quantity': 10, 'price': 150.0},
            {'ticker': 'GOOGL', 'quantity': 5, 'price': 2800.0},
            {'ticker': 'MSFT', 'quantity': 8, 'price': 350.0},
        ]

        for trade in trades:
            transaction_data = {
                'date': datetime.now(UTC).isoformat(),
                'ticker_id': tickers[trade['ticker']],
                'ticker2_id': 7,
                'quantity': str(trade['quantity']),
                'quantity2': str(trade['quantity'] * trade['price']),
                'price': str(trade['price']),
                'price_usd': str(trade['price']),
                'type': 'Buy',
                'portfolio_id': portfolio_id,
                'wallet_id': wallet_id,
                'comment': f"Покупка {trade['ticker']}",
            }

            response = await client.post('/api/transactions/', json=transaction_data, headers=auth_headers)
            assert response.status_code == status.HTTP_201_CREATED

        portfolio_response = await client.get(f'/api/portfolios/{portfolio_id}', headers=auth_headers)
