from app.modules.market.external_api.core import registry


def _currency_providers() -> list[str]:
    return [
        name
        for name, cls in registry.PROVIDERS.items()
        if cls.SUPPORTED_MARKETS == ['currency']
    ]


class TestCurrencyProviderContract:
    def test_currency_providers_register_currency_price_updater(self):
        providers = _currency_providers()
        assert providers, 'В реестре нет валютных провайдеров'

        for name in providers:
            by_method = {m['method']: m for m in registry.get_provider_methods(name)}
            update = by_method.get('update_prices')
            assert update is not None, f'{name}: метод update_prices не зарегистрирован'
            assert update['name'] == 'Обновление курсов валют', (
                f'{name}: update_prices зарегистрирован не с CurrencyPriceUpdater'
            )

    def test_currency_providers_do_not_register_ticker_loader(self):
        for name in _currency_providers():
            by_method = {m['method']: m for m in registry.get_provider_methods(name)}
            assert 'load_tickers' not in by_method, (
                f'{name}: load_tickers больше не нужен для валют (тикеры сидятся статически)'
            )
