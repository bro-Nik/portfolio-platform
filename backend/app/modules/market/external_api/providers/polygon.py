import asyncio
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
import logging

import httpx

from app.modules.market.external_api.core import BaseProvider, registry
from app.modules.market.external_api.methods import full_price_updater, image_loader, ticker_loader

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
    # Размер пачки для эндпоинтов без батчинга: держим в пределах дневной квоты,
    # чтобы уложиться в таймаут задачи.
    MAX_BATCH = 100

    SUPPORTED_MARKETS = ['stocks']

    @registry.register_method(ticker_loader)
    async def load_tickers(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await ticker_loader.run(market, self._fetch_all_tickers, **kwargs)

    @registry.register_method(full_price_updater)
    async def update_prices(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await full_price_updater.run(
            market,
            self._fetch_all_prices,
            quote_currency=self.QUOTE_CURRENCY,
            **kwargs,
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
                {'id': item.get('ticker'), 'symbol': item.get('ticker'), 'name': item.get('name')} for item in results
            ]
            logger.info('Загружено %s тикеров', len(batch))
            yield batch

            next_url = data.get('next_url')
            if not next_url:
                break

    async def _fetch_all_prices(self) -> dict[str, float]:
        # Дата считается в UTC: naive now() зависел от TZ контейнера и молча
        # сдвигала запрашиваемый торговый день.
        now = datetime.now(UTC)
        date = now.date()
        if now.hour < 12:
            date -= timedelta(days=1)

        for attempt in range(self.MAX_ATTEMPTS):
            date -= timedelta(days=1)
            logger.info('Попытка %s: запрос цен на %s', attempt + 1, date)
            try:
                params = self._augment_params({'adjusted': 'true'})
                data = await self.http.request(
                    'GET',
                    f'v2/aggs/grouped/locale/us/market/stocks/{date}',
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
        # Запросы идут пачками по MAX_BATCH: у провайдера 5 запросов в минуту,
        # и последовательный цикл на 300 тикерах физически не успевал — лимит
        # запросов истекал, задача падала по таймауту. Пачки идут последовательно,
        # параллелизм всё равно упёрся бы в квоту.
        image_urls: dict[str, str] = {}
        for start in range(0, len(ext_ids), self.MAX_BATCH):
            batch = ext_ids[start : start + self.MAX_BATCH]
            results = await asyncio.gather(
                *(self._fetch_one_image(ext_id) for ext_id in batch),
                return_exceptions=True,
            )
            for ext_id, result in zip(batch, results, strict=True):
                if isinstance(result, Exception):
                    logger.warning('Не удалось получить брендинг для %s: %s', ext_id, result)
                elif result:
                    image_urls[ext_id] = result
        return image_urls

    async def _fetch_one_image(self, ext_id: str) -> str | None:
        data = await self.http.request(
            'GET',
            f'v3/reference/tickers/{ext_id}',
            params=self._augment_params(),
        )
        branding = data.get('results', {}).get('branding')
        return branding.get('icon_url') if branding else None
