from decimal import Decimal

from app.modules.market.external_api.providers.yahoo import US_SCREENER_IDS, YahooProvider


def make_provider(async_mock, payload):
    http = async_mock()
    http.request = async_mock(return_value=payload)
    return YahooProvider(http), http


def screener_payload(*quotes: dict) -> dict:
    return {'finance': {'result': [{'quotes': list(quotes)}]}}

def equity(symbol, name):
    return {'symbol': symbol, 'quoteType': 'EQUITY', 'shortName': name}

def bond(symbol):
    return {'symbol': symbol, 'quoteType': 'EQUITY', 'shortName': None}

def spark_item(close):
    return {'timestamp': [1786541400], 'close': [close]}


class TestYahooProviderLoadTickers:
    async def test_filters_bonds_and_missing_names(self, async_mock):
        payload = screener_payload(
            equity('AAPL', 'Apple Inc.'),
            bond('XS1824248899.SG'),
            equity('VOW3.DE', 'Volkswagen AG'),
            {'symbol': 'ZZZZ', 'quoteType': 'BOND', 'shortName': 'Bond'},
        )
        provider, _ = make_provider(async_mock, payload)

        batches = [batch async for batch in provider._fetch_all_tickers()]

        assert batches == [[
            {'id': 'AAPL', 'symbol': 'AAPL', 'name': 'Apple Inc.'},
            {'id': 'VOW3.DE', 'symbol': 'VOW3.DE', 'name': 'Volkswagen AG'},
        ]]

    async def test_paginates_until_short_page(self, async_mock):
        page1 = screener_payload(*[equity(f'S{i}', f'Name {i}') for i in range(250)])
        short = screener_payload(equity('AAPL', 'Apple Inc.'))
        http = async_mock()
        http.request = async_mock(side_effect=[page1] + [short] * 100)
        provider = YahooProvider(http)

        batches = [batch async for batch in provider._fetch_all_tickers()]

        assert len(batches) == 2
        assert sum(len(b) for b in batches) == 251
        starts = [c.kwargs['params']['start'] for c in http.request.await_args_list]
        assert starts[0] == 0
        assert starts[1] == 250

    async def test_dedupes_symbols_across_pages(self, async_mock):
        page1 = screener_payload(*[equity('AAPL', 'Apple Inc.')] + [equity(f'S{i}', f'Name {i}') for i in range(250)])
        page2 = screener_payload(equity('AAPL', 'Apple Inc.'), equity('MSFT', 'Microsoft'))
        http = async_mock()
        http.request = async_mock(side_effect=[page1, page2])
        provider = YahooProvider(http)

        batches = [batch async for batch in provider._fetch_all_tickers()]

        assert batches[1] == [{'id': 'MSFT', 'symbol': 'MSFT', 'name': 'Microsoft'}]
        all_symbols = [t['symbol'] for b in batches for t in b]
        assert all_symbols.count('AAPL') == 1

    async def test_us_uses_multiple_screeners(self, async_mock):
        payloads = [
            screener_payload(equity(f'S{i}', f'Name {i}'))
            for i in range(len(US_SCREENER_IDS))
        ]
        http = async_mock()
        http.request = async_mock(side_effect=payloads + [screener_payload()] * 100)
        provider = YahooProvider(http)

        batches = [batch async for batch in provider._fetch_all_tickers()]

        assert len(batches) == len(US_SCREENER_IDS)
        scr_ids = [c.kwargs['params']['scrIds'] for c in http.request.await_args_list][:8]
        assert scr_ids == US_SCREENER_IDS
        assert all('marketRegion' not in c.kwargs['params'] for c in http.request.await_args_list[:8])

    async def test_passes_market_region(self, async_mock):
        empty = screener_payload()
        http = async_mock()
        http.request = async_mock(
            side_effect=[empty] * 8 + [screener_payload(equity('VOW3.DE', 'Volkswagen AG'))] + [empty] * 100,
        )
        provider = YahooProvider(http)

        batches = [batch async for batch in provider._fetch_all_tickers()]

        assert batches
        region_calls = [
            c for c in http.request.await_args_list
            if c.kwargs['params'].get('marketRegion') == 'DE'
        ]
        assert region_calls

    async def test_skips_on_http_error(self, async_mock):
        http = async_mock()
        http.request = async_mock(side_effect=RuntimeError('boom'))
        provider = YahooProvider(http)

        batches = [batch async for batch in provider._fetch_all_tickers()]

        assert batches == []


class TestYahooProviderGetPrices:
    async def test_usd_symbols_pass_through(self, async_mock):
        payload = {'AAPL': spark_item(302.25), 'MSFT': spark_item(499.86)}
        provider, _ = make_provider(async_mock, payload)

        prices = await provider.get_prices(['AAPL', 'MSFT'])

        assert prices == {'AAPL': Decimal('302.25'), 'MSFT': Decimal('499.86')}

    async def test_converts_eur_and_gbp_to_usd(self, async_mock):
        payload = {
            'AAPL': spark_item(302.25),
            'VOW3.DE': spark_item(73.28),
            'HSBA.L': spark_item(900.5),
            'EURUSD=X': spark_item(1.153),
            'GBPUSD=X': spark_item(1.349),
        }
        provider, _ = make_provider(async_mock, payload)

        prices = await provider.get_prices(['AAPL', 'VOW3.DE', 'HSBA.L'])

        assert prices == {
            'AAPL': Decimal('302.25'),
            'VOW3.DE': Decimal('84.49184'),
            'HSBA.L': Decimal('1214.7745'),
        }

    async def test_divides_quoted_pairs(self, async_mock):
        payload = {
            '0700.HK': spark_item(300.0),
            '7203.T': spark_item(1500.0),
            'USDHKD=X': spark_item(7.8463),
            'USDJPY=X': spark_item(159.372),
        }
        provider, _ = make_provider(async_mock, payload)

        prices = await provider.get_prices(['0700.HK', '7203.T'])

        assert prices == {
            '0700.HK': Decimal('38.23458190484687'),
            '7203.T': Decimal('9.411941871846999'),
        }

    async def test_skips_missing_close(self, async_mock):
        payload = {
            'AAPL': spark_item(302.25),
            'MSFT': {'timestamp': [1], 'close': []},
        }
        provider, _ = make_provider(async_mock, payload)

        prices = await provider.get_prices(['AAPL', 'MSFT'])

        assert prices == {'AAPL': Decimal('302.25')}

    async def test_skips_unknown_currency(self, async_mock):
        payload = {'TSLA.MX': spark_item(1000.0)}
        provider, _ = make_provider(async_mock, payload)

        prices = await provider.get_prices(['TSLA.MX'])

        assert prices == {}

    async def test_skips_missing_fx_rate(self, async_mock):
        payload = {'VOW3.DE': spark_item(73.28)}
        provider, _ = make_provider(async_mock, payload)

        prices = await provider.get_prices(['VOW3.DE'])

        assert prices == {}

    async def test_chunks_symbols_by_20(self, async_mock):
        payload = {f'S{i}.DE': spark_item(10.0) for i in range(25)}
        payload['EURUSD=X'] = spark_item(1.0)
        provider, http = make_provider(async_mock, payload)

        prices = await provider.get_prices([f'S{i}.DE' for i in range(25)])

        assert len(prices) == 25
        assert len(http.request.await_args_list) == 3
        chunks = [c.kwargs['params']['symbols'] for c in http.request.await_args_list]
        assert len(chunks[0].split(',')) == 20
        assert len(chunks[1].split(',')) == 5

    async def test_empty_on_http_error(self, async_mock):
        http = async_mock()
        http.request = async_mock(side_effect=RuntimeError('boom'))
        provider = YahooProvider(http)

        prices = await provider.get_prices(['AAPL'])

        assert prices == {}

    async def test_empty_without_ids(self, async_mock):
        provider, http = make_provider(async_mock, {})

        prices = await provider.get_prices([])

        assert prices == {}
        assert not http.request.called
