from app.modules.market.external_api.providers.currencyapi import CurrencyApiProvider


def make_provider(async_mock, payload):
    http = async_mock()
    http.request = async_mock(return_value=payload)
    return CurrencyApiProvider(http), http


class TestCurrencyApiProvider:
    async def test_live_rates_keys_normalized_to_iso(self, async_mock):
        rates = {'usd': 1.0, 'eur': 0.85, 'aed': 3.6725, 'btc': 0.0000129}
        provider, _ = make_provider(async_mock, {'date': '2026-04-29', 'usd': rates})

        result = await provider._fetch_live_rates()

        assert result == {
            'USD': round(1.0 / 1.0, 10),
            'EUR': round(1.0 / 0.85, 10),
            'AED': round(1.0 / 3.6725, 10),
            'BTC': round(1.0 / 0.0000129, 10),
        }

    async def test_live_rates_no_data(self, async_mock):
        provider, _ = make_provider(async_mock, {'date': '2026-04-29', 'usd': {}})

        result = await provider._fetch_live_rates()

        assert result == {}

    async def test_live_rates_skip_zero_values(self, async_mock):
        provider, _ = make_provider(async_mock, {'usd': {'eur': 0.0, 'aed': 3.67}})

        result = await provider._fetch_live_rates()

        assert result == {'AED': round(1.0 / 3.67, 10)}
