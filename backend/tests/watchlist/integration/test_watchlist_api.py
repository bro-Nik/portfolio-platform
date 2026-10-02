from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, patch

from fastapi import status

from app.modules.auth.models import User
from app.modules.auth.repositories import UserEmailRepository
from app.modules.watchlist.models import PriceAlert, WatchlistItem
from app.modules.watchlist.services.alert_evaluator import AlertEvaluatorService


class TestWatchlistAPI:
    async def test_add_item(self, client, auth_headers, btc):
        response = await client.post('/api/watchlist', json={'tickerId': btc.id}, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['tickerId'] == btc.id
        assert data['symbol'] == 'BTC'
        assert data['price'] == 60000.0
        assert data['alerts'] == []

    async def test_add_duplicate_item_conflicts(self, client, auth_headers, watchlist_item):
        response = await client.post(
            '/api/watchlist', json={'tickerId': watchlist_item.ticker_id}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_add_unknown_ticker_not_found(self, client, auth_headers):
        response = await client.post('/api/watchlist', json={'tickerId': 999999}, headers=auth_headers)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_list_items(self, client, auth_headers, watchlist_item, db_session, save, eth, user):
        await save(db_session, WatchlistItem(user_id=user.id, ticker_id=eth.id))

        response = await client.get('/api/watchlist', headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        items = response.json()['items']
        assert len(items) == 2
        assert {i['symbol'] for i in items} == {'BTC', 'ETH'}

    async def test_update_comment(self, client, auth_headers, watchlist_item):
        response = await client.put(
            f'/api/watchlist/{watchlist_item.id}', json={'comment': 'новый'}, headers=auth_headers
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json()['comment'] == 'новый'

    async def test_delete_item_cascades_alerts(self, client, auth_headers, db_session, alert, watchlist_item):
        item_id, alert_id = watchlist_item.id, alert.id
        response = await client.delete(f'/api/watchlist/{item_id}', headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Bulk-DELETE не чистит identity map: сбрасываем кеш сессии перед проверкой.
        db_session.expire_all()
        assert await db_session.get(WatchlistItem, item_id) is None
        assert await db_session.get(PriceAlert, alert_id) is None

    async def test_foreign_item_returns_404(self, client, auth_headers, db_session, save, btc):
        other = await save(db_session, User(email='other@example.com', password_hash='x', is_verified=True))
        foreign = await save(db_session, WatchlistItem(user_id=other.id, ticker_id=btc.id))

        for method, kwargs in [
            ('put', {'json': {'comment': 'x'}}),
            ('delete', {}),
            ('patch', {'json': {'isArchived': True}}),
        ]:
            response = await getattr(client, method)(f'/api/watchlist/{foreign.id}', headers=auth_headers, **kwargs)
            assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAlertsAPI:
    async def test_create_alert_derives_direction(self, client, auth_headers, watchlist_item):
        response = await client.post(
            f'/api/watchlist/{watchlist_item.id}/alerts',
            json={'targetPriceUsd': '50000'},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['direction'] == 'below'
        assert data['isActive'] is True

    async def test_create_alert_invalid_target(self, client, auth_headers, watchlist_item):
        response = await client.post(
            f'/api/watchlist/{watchlist_item.id}/alerts',
            json={'direction': 'above', 'targetPriceUsd': '0'},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_list_item_alerts(self, client, auth_headers, alert, watchlist_item):
        response = await client.get(f'/api/watchlist/{watchlist_item.id}/alerts', headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1

    async def test_update_alert_rearms(self, client, auth_headers, db_session, alert):
        alert.is_active = False
        alert.triggered_at = datetime.now(UTC)
        alert.triggered_price = 71000.0
        await db_session.flush()

        response = await client.put(f'/api/watchlist/alerts/{alert.id}', json={'isActive': True}, headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['isActive'] is True
        assert data['triggeredAt'] is None

    async def test_delete_alert(self, client, auth_headers, db_session, alert):
        response = await client.delete(f'/api/watchlist/alerts/{alert.id}', headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert await db_session.get(PriceAlert, alert.id) is None

    async def test_triggered_list(self, client, auth_headers, db_session, alert):
        alert.is_active = False
        alert.triggered_at = datetime.now(UTC)
        alert.triggered_price = 71000.0
        await db_session.flush()

        response = await client.get('/api/watchlist/alerts/triggered', headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        alerts = response.json()['alerts']
        assert len(alerts) == 1
        assert alerts[0]['tickerSymbol'] == 'BTC'
        assert alerts[0]['currentPrice'] == 60000.0

    async def test_unauthenticated(self, client):
        response = await client.get('/api/watchlist')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAlertEvaluationFlow:
    async def test_price_update_triggers_alert_end_to_end(self, db_session, user, btc, alert):
        evaluator = AlertEvaluatorService(db_session, UserEmailRepository(db_session))

        with patch('app.modules.watchlist.services.alert_evaluator.send_price_alert_email') as task:
            task.kiq = AsyncMock()
            await evaluator.on_prices_updated({btc.id: 71000.0})

        await db_session.refresh(alert)
        assert alert.is_active is False
        assert alert.triggered_price == 71000.0
        assert alert.triggered_at is not None
        task.kiq.assert_awaited_once_with(alert_id=alert.id, email='test@example.com')

    async def test_second_run_does_not_resend(self, db_session, user, btc, alert):
        evaluator = AlertEvaluatorService(db_session, UserEmailRepository(db_session))

        with patch('app.modules.watchlist.services.alert_evaluator.send_price_alert_email') as task:
            task.kiq = AsyncMock()
            await evaluator.on_prices_updated({btc.id: 71000.0})
            task.kiq.reset_mock()
            await evaluator.on_prices_updated({btc.id: 72000.0})

        task.kiq.assert_not_awaited()

    async def test_unverified_user_gets_no_email_but_alert_triggers(self, db_session, btc, save):
        unverified = await save(db_session, User(email='new@example.com', password_hash='x', is_verified=False))
        item = await save(db_session, WatchlistItem(user_id=unverified.id, ticker_id=btc.id))
        alert = await save(
            db_session,
            PriceAlert(
                watchlist_item_id=item.id,
                user_id=unverified.id,
                direction='above',
                target_price_usd=Decimal(70000),
                currency_symbol='USD',
            ),
        )
        evaluator = AlertEvaluatorService(db_session, UserEmailRepository(db_session))

        with patch('app.modules.watchlist.services.alert_evaluator.send_price_alert_email') as task:
            task.kiq = AsyncMock()
            await evaluator.on_prices_updated({btc.id: 71000.0})

        await db_session.refresh(alert)
        assert alert.is_active is False
        task.kiq.assert_not_awaited()
