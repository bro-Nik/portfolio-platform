from unittest.mock import patch

from app.modules.market.external_api.methods import price_updaters
from app.modules.market.external_api.methods.price_updaters import CurrencyPriceUpdater, FullPriceUpdater


class TestCurrencyPriceUpdater:
    async def test_resolves_by_symbol(self, async_mock, mock):
        prices = {'USD': 1.0, 'EUR': 1.1}
        fetch_prices = async_mock(return_value=prices)
        ticker_service = mock()
        ticker_service.resolve_prices_by_symbol = async_mock(return_value={1: 1.0, 2: 1.1})
        ticker_service.save_prices = async_mock(return_value=2)

        result = await CurrencyPriceUpdater().run('currency', fetch_prices, provider_name='CurrencyLayer', ticker_service=ticker_service)

        assert result == {'status': 'success', 'message': 'Обновлено 2 цен'}
        ticker_service.resolve_prices_by_symbol.assert_awaited_once_with('currency', prices)
        ticker_service.save_prices.assert_awaited_once_with('currency', {1: 1.0, 2: 1.1}, provider_name='CurrencyLayer')

    async def test_empty_prices_returns_error(self, async_mock, mock):
        fetch_prices = async_mock(return_value={})
        ticker_service = mock()

        result = await CurrencyPriceUpdater().run('currency', fetch_prices, provider_name='CurrencyLayer', ticker_service=ticker_service)

        assert result == {'status': 'error', 'message': 'Нет данных от провайдера'}
        ticker_service.save_prices.assert_not_called()


class TestFullPriceUpdater:
    async def test_resolves_by_external_id(self, async_mock, mock):
        fetch_prices = async_mock(return_value={'AAPL': 150.0})
        ticker_service = mock()
        ticker_service.save_prices = async_mock(return_value=1)

        with patch.object(price_updaters, 'TickerExternalIdService') as ext_id_service:
            ext_id_service.return_value.resolve_to_internal = async_mock(return_value={700: 150.0})
            result = await FullPriceUpdater().run('stocks', fetch_prices, provider_name='Polygon', ticker_service=ticker_service)

        assert result['status'] == 'success'
        ext_id_service.return_value.resolve_to_internal.assert_awaited_once_with('Polygon', {'AAPL': 150.0})
        ticker_service.save_prices.assert_awaited_once_with('stocks', {700: 150.0}, provider_name='Polygon')

    async def test_empty_prices_returns_error(self, async_mock, mock):
        fetch_prices = async_mock(return_value={})
        ticker_service = mock()

        result = await FullPriceUpdater().run('stocks', fetch_prices, provider_name='Polygon', ticker_service=ticker_service)

        assert result == {'status': 'error', 'message': 'Нет данных от провайдера'}
        ticker_service.save_prices.assert_not_called()
