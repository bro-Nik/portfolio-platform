from unittest.mock import AsyncMock

import pytest

from app.common.exceptions import ConflictError, NotFoundError
from app.modules.market.services.ticker import TickerService
from app.modules.watchlist.repositories import WatchlistItemRepository
from app.modules.watchlist.services.watchlist import WatchlistService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = WatchlistService(
        db_session,
        ctx,
        ticker_service=async_mock(spec=TickerService),
    )
    service.items = async_mock(spec=WatchlistItemRepository, session=db_session)
    return service


def _ticker(mock, ticker_id=1):
    return mock(id=ticker_id, name='Bitcoin', symbol='BTC', market='crypto', price=60000.0)


def _item(mock, item_id=1, ticker_id=1):
    item = mock(id=item_id, ticker_id=ticker_id, comment=None, user_id=user_id, is_archived=False)
    item.alerts = []
    return item


class TestWatchlistService:
    async def test_get_all_enriches_ticker_info(self, service, mock):
        items = [_item(mock, 1, 1), _item(mock, 2, 2)]
        service.items.get_by_user = AsyncMock(return_value=items)
        service.tickers.get_info = AsyncMock(
            return_value={1: mock(name='Bitcoin', symbol='BTC', image=None, market='crypto')}
        )
        service.tickers.get_prices = AsyncMock(return_value={1: 60000.0, 2: 3000.0})

        result = await service.get_all()

        assert result == items
        service.items.get_by_user.assert_awaited_once_with(user_id)
        assert items[0].symbol == 'BTC'
        assert items[0].price == 60000.0
        assert items[1].price == 3000.0

    async def test_create_ok(self, service, mock):
        service.tickers.get = AsyncMock(return_value=_ticker(mock))
        service.items.exists_for_user = AsyncMock(return_value=False)
        created = _item(mock)
        service.items.create = AsyncMock(return_value=created)
        service.items.get_own = AsyncMock(return_value=created)
        service.tickers.get_info = AsyncMock(return_value={})
        service.tickers.get_prices = AsyncMock(return_value={})

        result = await service.create(1, 'комментарий')

        assert result == created
        service.items.create.assert_awaited_once_with({'ticker_id': 1, 'comment': 'комментарий', 'user_id': user_id})

    async def test_create_unknown_ticker(self, service):
        service.tickers.get = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.create(999)

    async def test_create_duplicate(self, service, mock):
        service.tickers.get = AsyncMock(return_value=_ticker(mock))
        service.items.exists_for_user = AsyncMock(return_value=True)

        with pytest.raises(ConflictError):
            await service.create(1)

    async def test_update_foreign_raises(self, service):
        service.items.get_own = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.update(999, 'x')

    async def test_delete_foreign_raises(self, service):
        service.items.get_own = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.delete(999)

    async def test_archive_foreign_raises(self, service):
        service.items.get_own = AsyncMock(return_value=None)

        with pytest.raises(NotFoundError):
            await service.archive(999, True)
