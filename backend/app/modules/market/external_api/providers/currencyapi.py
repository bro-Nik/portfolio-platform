import logging

from ..core import BaseProvider, registry
from ..methods import currency_price_updater

logger = logging.getLogger(__name__)


@registry.register_provider()
class CurrencyApiProvider(BaseProvider):
    NAME = 'CurrencyApi'
    DESCRIPTION = 'Валюты'
    BASE_URL = 'https://cdn.jsdelivr.net/gh/irfanokr/currency-api@main/v1/currencies/'
    API_KEY_REQUIRED = False

    REQUESTS_PER_MINUTE = 5
    REQUESTS_PER_HOUR = 5
    REQUESTS_PER_DAY = 5
    REQUESTS_PER_MONTH = 150
    TIMEOUT = 30

    SUPPORTED_MARKETS = ['currency']

    @registry.register_method(currency_price_updater)
    async def update_prices(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await currency_price_updater.run(market, self._fetch_live_rates, **kwargs)

    async def _fetch_live_rates(self) -> dict[str, float]:
        try:
            data = await self.http.request('GET', 'usd.min.json')
        except Exception:
            logger.exception('Ошибка загрузки курсов валют')
            return {}

        rates = data.get('usd', {})
        if not rates:
            logger.error('Нет данных о курсах')
            return {}

        result = {}
        for code, rate in rates.items():
            if isinstance(rate, (int, float)) and rate != 0:
                result[code.upper()] = round(1.0 / float(rate), 10)

        return result
