from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.common.exceptions import BusinessRuleError, NotFoundError
from app.modules.market.services.ticker import TickerService
from app.modules.watchlist.repositories import PriceAlertRepository, WatchlistItemRepository
from app.modules.watchlist.services.alert import AlertService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = AlertService(
        db_session,
        ctx,
        ticker_service=async_mock(spec=TickerService),
    )
    service.alerts = async_mock(spec=PriceAlertRepository, session=db_session)
    service.items = async_mock(spec=WatchlistItemRepository, session=db_session)
    return service


def _item(mock, item_id=1, ticker_id=1):
    return mock(id=item_id, ticker_id=ticker_id, user_id=user_id)


def _alert(mock, alert_id=1, direction='above'):
    return mock(
        id=alert_id,
        watchlist_item_id=1,
        user_id=user_id,
        direction=direction,
        target_price_usd=Decimal(100),
        currency_symbol='USD',
        is_active=True,
    )


class TestAlertService:
    async def test_create_with_explicit_direction(self, service, mock):
        service.items.get_own = AsyncMock(return_value=_item(mock))
        created = _alert(mock)
        service.alerts.create = AsyncMock(return_value=created)

        result = await service.create(1, direction='above', target_price_usd=Decimal(70000))

        assert result == created
        service.alerts.create.assert_awaited_once_with(
            {
                'watchlist_item_id': 1,
                'user_id': user_id,
                'direction': 'above',
                'target_price_usd': Decimal(70000),
                'currency_symbol': 'USD',
                'comment': None,
            }
        )

    async def test_create_derives_down_when_target_below_price(self, service, mock):
        service.items.get_own = AsyncMock(return_value=_item(mock))
        service.tickers.get_prices = AsyncMock(return_value={1: 60000.0})
        service.alerts.create = AsyncMock(return_value=_alert(mock, direction='below'))

        await service.create(1, direction=None, target_price_usd=Decimal(50000))

        payload = service.alerts.create.await_args.args[0]
        assert payload['direction'] == 'below'

    async def test_create_derives_up_when_target_above_price(self, service, mock):
        service.items.get_own = AsyncMock(return_value=_item(mock))
        service.tickers.get_prices = AsyncMock(return_value={1: 60000.0})
        service.alerts.create = AsyncMock(return_value=_alert(mock, direction='above'))

        await service.create(1, direction=None, target_price_usd=Decimal(70000))

        payload = service.alerts.create.await_args.args[0]
        assert payload['direction'] == 'above'

    async def test_create_without_price_requires_direction(self, service, mock):
        service.items.get_own = AsyncMock(return_value=_item(mock))
        service.tickers.get_prices = AsyncMock(return_value={})

        with pytest.raises(BusinessRuleError):
            await service.create(1, direction=None, target_price_usd=Decimal(50000))

    async def test_create_zero_target_rejected(self, service, mock):
        service.items.get_own = AsyncMock(return_value=_item(mock))

        with pytest.raises(BusinessRuleError):
            await service.create(1, direction='above', target_price_usd=Decimal(0))

    async def test_create_foreign_item_raises(self, service, mock):
        service.items.get_own = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.create(999, direction='above', target_price_usd=Decimal(1))

    async def test_update_rearm_clears_trigger(self, service, mock):
        alert = _alert(mock)
        alert.triggered_at = '2026-01-01'
        alert.triggered_price = 61000.0
        alert.is_active = False
        service.alerts.get_own = AsyncMock(return_value=alert)
        service.alerts.update = AsyncMock(return_value=alert)

        await service.update(1, is_active=True)

        service.alerts.update.assert_awaited_once_with(
            1, {'is_active': True, 'triggered_at': None, 'triggered_price': None}
        )

    async def test_delete_foreign_raises(self, service):
        service.alerts.get_own = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.delete(999)
