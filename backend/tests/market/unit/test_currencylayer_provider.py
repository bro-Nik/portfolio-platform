from pathlib import Path

from app.modules.market.external_api.providers.currencylayer import CurrencyLayerProvider

STATIC_DIR = Path(__file__).resolve().parents[3] / 'static'


def make_provider(async_mock, payload):
    http = async_mock()
    http.request = async_mock(return_value=payload)
    return CurrencyLayerProvider(http), http


class TestCurrencyLayerProvider:
    async def test_load_tickers_filters_to_curated_codes(self, async_mock):
        currencies = {code: f'Name {code}' for code in ['USD', 'EUR', 'ZWL', 'AED', 'XDR']}
        provider, _ = make_provider(async_mock, {'currencies': currencies})

        batches = []
        async for batch in provider._fetch_all_tickers():
            batches.extend(batch)

        symbols = {item['symbol'] for item in batches}
        assert symbols == {'USD', 'EUR', 'AED'}
        assert all(item['id'] == item['symbol'].lower() for item in batches)

    async def test_load_tickers_empty_response(self, async_mock):
        provider, _ = make_provider(async_mock, {'currencies': {}})

        batches = []
        async for batch in provider._fetch_all_tickers():
            batches.extend(batch)

        assert batches == []

    async def test_live_rates_not_filtered(self, async_mock):
        quotes = {'USDZWL': 321.5, 'USDEUR': 0.85, 'USDAED': 3.67}
        provider, _ = make_provider(async_mock, {'quotes': quotes})

        rates = await provider._fetch_live_rates()

        assert rates == {'zwl': round(1.0 / 321.5, 10), 'eur': round(1.0 / 0.85, 10), 'aed': round(1.0 / 3.67, 10)}
