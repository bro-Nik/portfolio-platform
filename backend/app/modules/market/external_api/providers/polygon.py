from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
import logging

import httpx

from ..core import BaseProvider, registry
from ..methods import full_price_updater, image_loader, ticker_loader

logger = logging.getLogger(__name__)


@registry.register_provider()
class PolygonProvider(BaseProvider):
    NAME = 'Polygon'
    DESCRIPTION = 'Акции США'
    BASE_URL = 'https://api.polygon.io/'
    API_KEY_REQUIRED = True

    @classmethod
    def validate_config(cls, api_key: str | None) -> list[str]:
        issues = []
        if not api_key:
            issues.append('Требуется API ключ')
        return issues

    REQUESTS_PER_MINUTE = 5
    REQUESTS_PER_HOUR = 60
    REQUESTS_PER_DAY = 200
    REQUESTS_PER_MONTH = 5000
    TIMEOUT = 30

    MAX_ATTEMPTS = 5

    SUPPORTED_MARKETS = ['stocks']

    @registry.register_method(ticker_loader)
    async def load_tickers(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await ticker_loader.run(market, self._fetch_all_tickers, **kwargs)

    @registry.register_method(full_price_updater)
    async def update_prices(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await full_price_updater.run(
            market, self._fetch_all_prices, quote_currency=self.QUOTE_CURRENCY, **kwargs,
        )

    @registry.register_method(image_loader)
    async def load_images(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await image_loader.run(market, self._fetch_ticker_images, **kwargs)

    def _augment_params(self, params: dict | None = None) -> dict:
        p = dict(params or {})
        if self._api_key:
            p['apiKey'] = self._api_key
        return p

    async def _fetch_all_tickers(self) -> AsyncIterator[list[dict]]:
        next_url: str | None = None

        while True:
            params = self._augment_params({'market': 'stocks', 'limit': 1000, 'active': 'true'})
            try:
                if next_url:
                    url = httpx.URL(next_url).copy_with(params={'apiKey': self._api_key})
                    data = await self.http.request('GET', str(url))
                else:
                    data = await self.http.request('GET', 'v3/reference/tickers', params=params)
            except Exception:
                logger.exception('Ошибка загрузки тикеров')
                break

            results = data.get('results', [])
            batch = [
                {'id': item.get('ticker'), 'symbol': item.get('ticker'), 'name': item.get('name')}
                for item in results
            ]
            logger.info('Загружено %s тикеров', len(batch))
            yield batch

            next_url = data.get('next_url')
            if not next_url:
                break

    async def _fetch_all_prices(self) -> dict[str, float]:
        date = datetime.now().date()
        if datetime.now(UTC).hour < 12:
            date -= timedelta(days=1)

        for attempt in range(self.MAX_ATTEMPTS):
            date -= timedelta(days=1)
            logger.info('Попытка %s: запрос цен на %s', attempt + 1, date)
            try:
                params = self._augment_params({'adjusted': 'true'})
                data = await self.http.request(
                    'GET', f'v2/aggs/grouped/locale/us/market/stocks/{date}',
                    params=params,
                )
            except Exception:
                logger.exception('Ошибка запроса цен на %s', date)
                continue

            results = data.get('results')
            if results:
                logger.info('Получено цен: %s', len(results))
                return {item['T']: float(item['c']) for item in results}

        logger.error('Не удалось получить цены после %s попыток', self.MAX_ATTEMPTS)
        return {}

    async def _fetch_ticker_images(self, ext_ids: list[str]) -> dict[str, str]:
        image_urls = {}
        for ext_id in ext_ids:
            try:
                params = self._augment_params()
                data = await self.http.request(
                    'GET', f'v3/reference/tickers/{ext_id}',
                    params=params,
                )
            except Exception:
                logger.exception('Ошибка запроса брендинга для %s', ext_id)
                continue

            branding = data.get('results', {}).get('branding')
            icon_url = branding.get('icon_url') if branding else None
            if icon_url:
                image_urls[ext_id] = icon_url
                logger.info('Получена иконка для %s', ext_id)

        return image_urls
