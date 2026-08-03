from fastapi import status
import pytest

from app.modules.market.models import Ticker


class TestTickerSearchMarkets:
    @pytest.mark.usefixtures('tickers')
    async def test_search_by_single_market(self, client, auth_headers, db_session, save):
        await save(db_session, Ticker(id=100, name='US Dollar', symbol='USD', market='currency'))
        await db_session.commit()

        response = await client.get('/market/api/tickers', params={'markets': 'crypto'}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()['data']
        assert len(data) == 7
        assert all(t['market'] == 'crypto' for t in data)

    @pytest.mark.usefixtures('tickers')
    async def test_search_by_multiple_markets(self, client, auth_headers, db_session, save):
        await save(db_session, Ticker(id=100, name='US Dollar', symbol='USD', market='currency'))
        await save(db_session, Ticker(id=101, name='Euro', symbol='EUR', market='currency'))
        await db_session.commit()

        response = await client.get(
            '/market/api/tickers',
            params={'markets': ['crypto', 'currency']},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()['data']
        assert len(data) == 9
        assert {t['market'] for t in data} == {'crypto', 'currency'}

    @pytest.mark.usefixtures('tickers')
    async def test_search_without_markets_returns_all(self, client, auth_headers, db_session, save):
        await save(db_session, Ticker(id=100, name='US Dollar', symbol='USD', market='currency'))
        await db_session.commit()

        response = await client.get('/market/api/tickers', headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()['data']
        assert len(data) == 8

    @pytest.mark.usefixtures('tickers')
    async def test_search_mixed_market_and_search(self, client, auth_headers, db_session, save):
        await save(db_session, Ticker(id=100, name='US Dollar', symbol='USD', market='currency'))
        await save(db_session, Ticker(id=101, name='Tether', symbol='USDT', market='crypto'))
        await db_session.commit()

        response = await client.get(
            '/market/api/tickers',
            params={'markets': ['crypto', 'currency'], 'search': 'us'},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()['data']
        assert {t['symbol'] for t in data} == {'USD', 'USDT'}
