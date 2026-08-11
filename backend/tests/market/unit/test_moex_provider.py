from app.modules.market.external_api.providers.moex import MoexProvider


def make_provider(async_mock, payload):
    http = async_mock()
    http.request = async_mock(return_value=payload)
    return MoexProvider(http), http


class TestMoexProvider:
    async def test_load_tickers_filters_non_shares(self, async_mock):
        payload = {
            'securities': {
                'columns': ['SECID', 'SHORTNAME', 'SECTYPE'],
                'data': [
                    ['SBER', 'Сбербанк', '1'],
                    ['SNGSP', 'Сургнфгз-п', '2'],
                    ['AKAI', 'AKAI ETF', 'J'],
                    ['RU0005418747', 'ФондПервый', '9'],
                    ['RU000A0JUR61', 'ЗПИФДОМ.РФ', 'A'],
                    ['OKEY', 'OKEY-гдр', 'D'],
                ],
            },
        }
        provider, _ = make_provider(async_mock, payload)

        batches = [batch async for batch in provider._fetch_all_tickers()]

        assert batches == [[
            {'id': 'SBER', 'symbol': 'SBER', 'name': 'Сбербанк'},
            {'id': 'SNGSP', 'symbol': 'SNGSP', 'name': 'Сургнфгз-п'},
        ]]

    async def test_load_tickers_skips_on_http_error(self, async_mock):
        http = async_mock()
        http.request = async_mock(side_effect=RuntimeError('boom'))
        provider = MoexProvider(http)

        batches = [batch async for batch in provider._fetch_all_tickers()]

        assert batches == []

    async def test_prices_return_raw_rub(self, async_mock):
        payload = {
            'securities': {
                'columns': ['SECID', 'SHORTNAME', 'SECTYPE'],
                'data': [
                    ['SBER', 'Сбербанк', '1'],
                    ['GOLD', 'GOLD ETF', 'J'],
                ],
            },
            'marketdata': {
                'columns': ['SECID', 'LAST'],
                'data': [
                    ['SBER', 286.19],
                    ['GOLD', 99.3],
                ],
            },
        }
        provider, _ = make_provider(async_mock, payload)

        prices = await provider._fetch_all_prices()

        assert prices == {'SBER': 286.19}

    async def test_prices_skip_missing_last(self, async_mock):
        payload = {
            'securities': {
                'columns': ['SECID', 'SHORTNAME', 'SECTYPE'],
                'data': [
                    ['SBER', 'Сбербанк', '1'],
                    ['AKAI', 'АКИ акция', '1'],
                ],
            },
            'marketdata': {
                'columns': ['SECID', 'LAST'],
                'data': [
                    ['SBER', 286.19],
                    ['AKAI', None],
                ],
            },
        }
        provider, _ = make_provider(async_mock, payload)

        prices = await provider._fetch_all_prices()

        assert prices == {'SBER': 286.19}

    async def test_prices_empty_without_marketdata(self, async_mock):
        payload = {
            'securities': {
                'columns': ['SECID', 'SHORTNAME', 'SECTYPE'],
                'data': [['SBER', 'Сбербанк', '1']],
            },
            'marketdata': {
                'columns': ['SECID', 'LAST'],
                'data': [['SBER', None]],
            },
        }
        provider, _ = make_provider(async_mock, payload)

        prices = await provider._fetch_all_prices()

        assert prices == {}

    async def test_prices_empty_on_http_error(self, async_mock):
        http = async_mock()
        http.request = async_mock(side_effect=RuntimeError('boom'))
        provider = MoexProvider(http)

        prices = await provider._fetch_all_prices()

        assert prices == {}
