from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from app.modules.watchlist.services.alert_evaluator import AlertEvaluatorService

user_id = 1


def _alert(mock, alert_id=1, direction='above', target='100', ticker_id=1):
    alert = mock(
        id=alert_id,
        user_id=user_id,
        direction=direction,
        target_price_usd=Decimal(target),
        is_active=True,
    )
    alert.watchlist_item = mock(ticker_id=ticker_id)
    alert.triggered_at = None
    alert.triggered_price = None
    return alert


@pytest.fixture
async def service(db_session, async_mock):
    users = async_mock()
    users.get_emails = AsyncMock(return_value={user_id: 'user@example.com'})
    service = AlertEvaluatorService(db_session, users)
    service._alerts = async_mock()
    return service


@pytest.fixture
def kiq():
    with patch('app.modules.watchlist.services.alert_evaluator.send_price_alert_email') as task:
        task.kiq = AsyncMock()
        yield task.kiq


class TestAlertEvaluator:
    async def test_above_triggers_and_sends_email(self, service, mock, kiq):
        alert = _alert(mock, direction='above', target='100')
        service._alerts.get_active_by_ticker_ids = AsyncMock(return_value=[alert])

        await service.on_prices_updated({1: 120.0})

        assert alert.is_active is False
        assert alert.triggered_price == 120.0
        assert alert.triggered_at is not None
        service._session.commit.assert_awaited_once()
        kiq.assert_awaited_once_with(alert_id=1, email='user@example.com')

    async def test_below_triggers(self, service, mock, kiq):
        alert = _alert(mock, direction='below', target='100')
        service._alerts.get_active_by_ticker_ids = AsyncMock(return_value=[alert])

        await service.on_prices_updated({1: 90.0})

        assert alert.is_active is False
        kiq.assert_awaited_once()

    async def test_no_hit_no_commit(self, service, mock, kiq):
        alert = _alert(mock, direction='above', target='100')
        service._alerts.get_active_by_ticker_ids = AsyncMock(return_value=[alert])

        await service.on_prices_updated({1: 90.0})

        assert alert.is_active is True
        service._session.commit.assert_not_awaited()
        kiq.assert_not_awaited()

    async def test_zero_price_skipped(self, service, mock, kiq):
        alert = _alert(mock, direction='below', target='100')
        service._alerts.get_active_by_ticker_ids = AsyncMock(return_value=[alert])

        await service.on_prices_updated({1: 0.0})

        service._session.commit.assert_not_awaited()
        kiq.assert_not_awaited()

    async def test_missing_email_marks_triggered_without_letter(self, service, mock, kiq, caplog):
        alert = _alert(mock, direction='above', target='100')
        service._alerts.get_active_by_ticker_ids = AsyncMock(return_value=[alert])
        service._users.get_emails = AsyncMock(return_value={})

        await service.on_prices_updated({1: 120.0})

        assert alert.is_active is False
        kiq.assert_not_awaited()
        assert 'письмо пропущено' in caplog.text

    async def test_empty_prices_noop(self, service, kiq):
        await service.on_prices_updated({})

        kiq.assert_not_awaited()

    async def test_unknown_direction_never_hits(self, service, mock, kiq):
        alert = _alert(mock, direction='sideways', target='100')
        service._alerts.get_active_by_ticker_ids = AsyncMock(return_value=[alert])

        await service.on_prices_updated({1: 120.0})

        service._session.commit.assert_not_awaited()
        kiq.assert_not_awaited()
