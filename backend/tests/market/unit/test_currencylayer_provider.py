from app.modules.market.external_api.providers.currencylayer import CurrencyLayerProvider


def make_provider(async_mock, payload):
    http = async_mock()
    http.request = async_mock(return_value=payload)
    return CurrencyLayerProvider(http), http


class TestCurrencyLayerProvider:
    async def test_live_rates_keys_normalized_to_iso(self, async_mock):
        quotes = {'USDZWL': 321.5, 'USDEUR': 0.85, 'USDAED': 3.67}
        provider, _ = make_provider(async_mock, {'quotes': quotes})

        rates = await provider._fetch_live_rates()

        assert rates == {
            'ZWL': round(1.0 / 321.5, 10),
            'EUR': round(1.0 / 0.85, 10),
            'AED': round(1.0 / 3.67, 10),
        }

    async def test_live_rates_no_data(self, async_mock):
        provider, _ = make_provider(async_mock, {'quotes': {}})

        rates = await provider._fetch_live_rates()

        assert rates == {}
