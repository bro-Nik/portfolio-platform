from collections.abc import Iterator
from unittest.mock import patch

import pytest

from app.common.media_client import MediaClient
from app.modules.market.repositories import TickerRepository
from app.modules.market.schemas import TickerInfo, TickerUpdateRequest
from app.modules.market.services.ticker import INFO_CACHE_TTL, PRICE_CACHE_TTL, TickerService
from app.modules.market.services.ticker_external_id import TickerExternalIdService
from app.modules.market.services.ticker_identifier import TickerIdentifierService


def make_service(db_session, async_mock, redis=None):
    return TickerService(
        db_session,
        repo=async_mock(spec=TickerRepository, session=db_session),
        ext_id_service=async_mock(spec=TickerExternalIdService),
        identifier_service=async_mock(spec=TickerIdentifierService),
        redis=redis,
    )


@pytest.fixture
def redis(async_mock, mock):
    redis = async_mock()
    pipe = mock()
    pipe.execute = async_mock()
    ctx = mock()
    ctx.__aenter__ = async_mock(return_value=pipe)
    ctx.__aexit__ = async_mock()
    redis.pipeline = mock(return_value=ctx)
    return redis


@pytest.fixture
async def service(db_session, async_mock, redis):
    service = make_service(db_session, async_mock, redis=redis)
    service._ext_id_service.get_ext_to_ticker_map.return_value = {}
    return service


class TestTickerServiceCache:
    async def test_get_prices_miss_fetches_from_sql_and_writes_cache(self, service, redis, mock):
        tickers = [mock(id=1, price=10.5), mock(id=2, price=20.25)]
        redis.mget.return_value = [None, None]

        with patch.object(service.repo, 'get_all_by_ids', return_value=tickers) as get_all_by_ids:
            prices = await service.get_prices([1, 2])

        assert prices == {1: 10.5, 2: 20.25}
        get_all_by_ids.assert_awaited_once_with([1, 2])
        pipe = redis.pipeline.return_value.__aenter__.return_value
        pipe.set.assert_any_call('ticker:price:1', '10.5', ex=PRICE_CACHE_TTL)
        pipe.set.assert_any_call('ticker:price:2', '20.25', ex=PRICE_CACHE_TTL)
        pipe.execute.assert_awaited_once()

    async def test_get_prices_hit_skips_sql(self, service, redis):
        redis.mget.return_value = ['99.0']

        prices = await service.get_prices([1])

        assert prices == {1: 99.0}
        service.repo.get_all_by_ids.assert_not_awaited()

    async def test_get_prices_partial_hit_fetches_only_missing(self, service, redis, mock):
        redis.mget.return_value = ['99.0', None]
        tickers = [mock(id=2, price=5.0)]

        with patch.object(service.repo, 'get_all_by_ids', return_value=tickers) as get_all_by_ids:
            prices = await service.get_prices([1, 2])

        assert prices == {1: 99.0, 2: 5.0}
        get_all_by_ids.assert_awaited_once_with([2])

    async def test_get_prices_no_redis_uses_sql(self, db_session, async_mock, mock):
        service = make_service(db_session, async_mock, redis=None)
        tickers = [mock(id=1, price=7.0)]

        with patch.object(service.repo, 'get_all_by_ids', return_value=tickers):
            prices = await service.get_prices([1])

        assert prices == {1: 7.0}

    async def test_get_info_miss_fetches_from_sql_and_writes_cache(self, service, redis, mock):
        tickers = [mock(id=1, name='Bitcoin', symbol='BTC', market='crypto', image='1.png')]
        redis.mget.return_value = [None]

        with patch.object(service.repo, 'get_all_by_ids', return_value=tickers) as get_all_by_ids:
            info = await service.get_info([1])

        assert info == {
            1: TickerInfo(
                name='Bitcoin',
                symbol='BTC',
                image='/market/static/images/tickers/crypto/24/1.png',
                market='crypto',
            )
        }
        get_all_by_ids.assert_awaited_once_with([1])
        pipe = redis.pipeline.return_value.__aenter__.return_value
        pipe.set.assert_called_once_with(
            'ticker:info:1',
            '{"name":"Bitcoin","symbol":"BTC","image":"/market/static/images/tickers/crypto/24/1.png","market":"crypto"}',
            ex=INFO_CACHE_TTL,
        )
        pipe.execute.assert_awaited_once()

    async def test_get_info_hit_skips_sql(self, service, redis):
        redis.mget.return_value = ['{"name": "Bitcoin", "symbol": "BTC", "image": null}']

        info = await service.get_info([1])

        assert info == {1: TickerInfo(name='Bitcoin', symbol='BTC', image=None)}
        service.repo.get_all_by_ids.assert_not_awaited()

    async def test_get_images_omits_missing_image(self, service, redis, mock):
        tickers = [mock(id=1, name='X', symbol='X', market='crypto', image=None)]
        redis.mget.return_value = [None]

        with patch.object(service.repo, 'get_all_by_ids', return_value=tickers):
            images = await service.get_images([1])

        assert images == {}

    async def test_get_info_no_redis_uses_sql(self, db_session, async_mock, mock):
        service = make_service(db_session, async_mock, redis=None)
        tickers = [mock(id=1, name='Bitcoin', symbol='BTC', market='crypto', image=None)]

        with patch.object(service.repo, 'get_all_by_ids', return_value=tickers):
            info = await service.get_info([1])

        assert info == {1: TickerInfo(name='Bitcoin', symbol='BTC', image=None, market='crypto')}

    async def test_save_prices_invalidates_price_keys(self, service, redis):
        with patch.object(service.repo, 'update_ticker_prices', return_value=2) as update_ticker_prices:
            updated = await service.save_prices('crypto', {1: 100.0, 2: 200.0}, provider_name='CoinGecko')

        assert updated == 2
        update_ticker_prices.assert_awaited_once_with({1: 100.0, 2: 200.0}, price_updated_by='CoinGecko')
        service.session.commit.assert_awaited_once()
        redis.delete.assert_awaited_once_with('ticker:price:1', 'ticker:price:2')

    async def test_sync_tickers_invalidates_info_keys(self, service, redis, mock):
        async def raw_data():
            yield [{'id': 'btc', 'name': 'Bitcoin', 'symbol': 'BTC'}]

        with patch.object(service.repo, 'create', return_value=mock(id=1)):
            result = await service.sync_tickers('crypto', raw_data(), provider_name='CoinGecko')

        assert result['created'] == 1
        redis.delete.assert_awaited_once_with('ticker:info:1')

    async def test_load_images_commits_and_invalidates_info_keys(self, service, redis, mock):
        tickers = [mock(id=1, image=None)]
        service._ext_id_service.resolve_to_external.return_value = {1: 'btc'}

        async def fetch_images(ext_ids):
            return {'btc': 'https://example.com/1.png'}

        with (
            patch.object(service.repo, 'get_all_by_market_without_images', return_value=tickers),
            patch.object(service, '_process_image', return_value='1.png'),
            patch.object(MediaClient, 'download_batch', return_value={'https://example.com/1.png': b'data'}),
        ):
            loaded = await service.load_images('crypto', fetch_images, provider_name='Polygon')

        assert loaded == 1
        service.session.commit.assert_awaited_once()
        redis.delete.assert_awaited_once_with('ticker:info:1')


class TestTickerAdminCacheInvalidation:
    async def test_update_invalidates_info_key(self, service, redis, mock, async_mock):
        ticker = mock(id=1, name='Bitcoin', symbol='BTC')
        updated = mock(
            id=1,
            name='Bitcoin2',
            symbol='BTC',
            market='crypto',
            price=1.0,
            market_cap_rank=None,
            image=None,
            is_active=True,
            updated_at=None,
            price_updated_by=None,
        )
        service.repo.get = async_mock(return_value=ticker)
        service.repo.update = async_mock(return_value=updated)

        await service.update(1, TickerUpdateRequest(name='Bitcoin2'))

        service.repo.update.assert_awaited_once_with(1, {'name': 'Bitcoin2'})
        service.session.commit.assert_awaited_once()
        redis.delete.assert_awaited_once_with('ticker:info:1')

    async def test_delete_invalidates_info_and_price_keys(self, service, redis, mock):
        empty_result = mock()
        empty_result.scalar.return_value = 0
        service.session.execute.return_value = empty_result
        ticker = mock(id=1, image=None, market='crypto')
        service.repo.get.return_value = ticker

        await service.delete(1)

        service.repo.delete.assert_awaited_once_with(1)
        service.session.commit.assert_awaited_once()
        redis.delete.assert_any_call('ticker:info:1')
        redis.delete.assert_any_call('ticker:price:1')

    async def test_merge_invalidates_info_and_price_keys(self, service, redis, mock, async_mock):
        source = mock(
            id=1,
            image=None,
            market='crypto',
            name='A',
            symbol='A',
            price=1.0,
            market_cap_rank=None,
            is_active=True,
            updated_at=None,
            price_updated_by=None,
        )
        target = mock(
            id=2,
            image=None,
            market='crypto',
            name='B',
            symbol='B',
            price=2.0,
            market_cap_rank=None,
            is_active=True,
            updated_at=None,
            price_updated_by=None,
        )
        service.repo.get = async_mock(side_effect=[source, target, target])
        service.session.execute.return_value = EmptyRows()

        merged = await service.merge(1, 2)

        service.repo.delete.assert_awaited_once_with(1)
        service.session.commit.assert_awaited_once()
        assert merged.id == 2
        redis.delete.assert_any_call('ticker:info:1', 'ticker:info:2')
        redis.delete.assert_any_call('ticker:price:1', 'ticker:price:2')


class EmptyRows:
    def __iter__(self) -> Iterator:
        return iter(())

    def scalars(self) -> Iterator:
        return iter(())
