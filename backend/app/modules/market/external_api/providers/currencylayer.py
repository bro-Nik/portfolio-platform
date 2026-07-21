import logging

from ..core import BaseProvider, registry
from ..methods import bulk_price_updater, ticker_loader

logger = logging.getLogger(__name__)


@registry.register_provider()
class CurrencyLayerProvider(BaseProvider):
    NAME = 'CurrencyLayer'
    DESCRIPTION = 'Валюты'
    BASE_URL = 'http://api.currencylayer.com/'

    REQUESTS_PER_MINUTE = 10
    REQUESTS_PER_HOUR = 100
    REQUESTS_PER_DAY = 500
    REQUESTS_PER_MONTH = 10000
    TIMEOUT = 30

    @registry.register_method(ticker_loader)
    async def load_tickers(self, **kwargs) -> dict:
        return await ticker_loader.run('currency', self._fetch_all_tickers, **kwargs)

    @registry.register_method(bulk_price_updater)
    async def update_prices(self, **kwargs) -> dict:
        return await bulk_price_updater.run('currency', self._fetch_live_rates)

    def _augment_params(self, params: dict | None = None) -> dict:
        p = dict(params or {})
        if self._api_key:
            p['access_key'] = self._api_key
        return p

    async def _fetch_all_tickers(self) -> list[dict]:
        params = self._augment_params()
        try:
            data = await self.http.request('GET', 'list', params=params)
        except Exception:
            logger.exception('Ошибка загрузки списка валют')
            return []

        currencies = data.get('currencies', {})
        return [{'id': code.lower(), 'name': name, 'symbol': code}
                for code, name in currencies.items()]

    async def _fetch_live_rates(self) -> dict[str, float]:
        params = self._augment_params()
        try:
            data = await self.http.request('GET', 'live', params=params)
        except Exception:
            logger.exception('Ошибка загрузки курсов валют')
            return {}

        quotes = data.get('quotes', {})
        if not quotes:
            logger.error('Нет данных о курсах')
            return {}

        result = {}
        for pair, rate in quotes.items():
            if isinstance(rate, (int, float)) and rate != 0:
                code = pair.removeprefix('USD').lower()
                result[code] = round(1.0 / float(rate), 10)

        return result
