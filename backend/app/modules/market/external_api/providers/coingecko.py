from decimal import Decimal
import json
import logging

from ..core import BaseProvider, registry
from ..methods import selective_price_updater, ticker_loader
from ..url_chunker import chunk_ids_for_url

logger = logging.getLogger(__name__)

PLATFORMS_CACHE_KEY = 'cg:platforms:v1'
PLATFORMS_CACHE_TTL = 86400


@registry.register_provider()
class CoingeckoProvider(BaseProvider):
    NAME = 'CoinGecko'
    DESCRIPTION = 'Криптовалюты'
    BASE_URL = 'https://api.coingecko.com/api/v3'
    SUPPORTED_MARKETS = ['crypto']

    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_HOUR = 100
    REQUESTS_PER_DAY = 10000
    REQUESTS_PER_MONTH = 100000
    TIMEOUT = 30

    MAX_URL_LENGTH = 2048

    @registry.register_method(selective_price_updater)
    async def selective_price_update(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await selective_price_updater.run(market, self.get_prices, **kwargs)

    @registry.register_method(ticker_loader)
    async def load_tickers(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        platforms_map = await self._fetch_platforms_map()
        return await ticker_loader.run(
            market,
            lambda: self._fetch_all_tickers(platforms_map),
            extract_identifiers=self.extract_identifiers,
            **kwargs,
        )

    def extract_identifiers(self, coin: dict) -> dict[str, str]:
        platforms = coin.get('platforms', {}) or {}
        result = {}
        for chain, address in platforms.items():
            if address and isinstance(address, str):
                normalized_chain = chain.replace('-', '_').replace(' ', '_').lower()
                result[f'contract_{normalized_chain}'] = address.lower()
        return result

    async def _fetch_platforms_map(self) -> dict[str, dict]:
        if self._redis:
            cached = await self._redis.get(PLATFORMS_CACHE_KEY)
            if cached:
                logger.info('Загрузка платформ из Redis кеша')
                return json.loads(cached)

        logger.info('Загрузка карты платформ с контрактными адресами из API...')
        try:
            data = await self.http.request(
                'GET', 'coins/list',
                params={'include_platform': 'true'},
            )
            platforms_map = {}
            for coin in data or []:
                coin_id = coin.get('id')
                platforms = coin.get('platforms', {}) or {}
                if coin_id and any(platforms.values()):
                    platforms_map[coin_id] = platforms

            if self._redis:
                await self._redis.setex(PLATFORMS_CACHE_KEY, PLATFORMS_CACHE_TTL, json.dumps(platforms_map))

            logger.info('Загружено платформ для %s монет', len(platforms_map))
            return platforms_map
        except Exception:
            logger.exception('Ошибка загрузки платформ')
            return {}

    async def _fetch_all_tickers(self, platforms_map: dict[str, dict] | None = None) -> list[dict]:
        all_coins = []
        page = 1
        while True:
            logger.info('Загрузка страницы тикеров %s...', page)
            try:
                data = await self.http.request(
                    'GET', 'coins/markets',
                    params={'vs_currency': 'usd', 'per_page': 250, 'page': page},
                )
            except Exception:
                logger.exception('Ошибка загрузки страницы %s', page)
                break
            if not data:
                break
            for coin in data:
                if platforms_map:
                    coin['platforms'] = platforms_map.get(coin.get('id'), {})
            all_coins.extend(data)
            if len(data) < 250:
                break
            page += 1
        logger.info('Загружено %s монет с CoinGecko', len(all_coins))
        return all_coins

    async def fetch_all_tickers(self) -> list[dict]:
        return await self._fetch_all_tickers()

    async def get_prices(self, ids: list[str]) -> dict[str, Decimal]:
        if not ids:
            return {}
        url = f'{self.BASE_URL}/simple/price?vs_currencies=usd&ids='
        chunks = chunk_ids_for_url(ids, url, self.MAX_URL_LENGTH)
        failed_chunks = []
        all_prices = {}
        for i, chunk in enumerate(chunks, 1):
            try:
                data = await self.http.request(
                    'GET', 'simple/price',
                    params={'vs_currencies': 'usd', 'ids': ','.join(chunk)},
                )
                all_prices.update(data)
                logger.info('Чанк %s/%s: %s монет', i, len(chunks), len(chunk))
            except Exception as e:
                logger.exception('Чанк упал')
                failed_chunks.append({'chunk': i, 'ids': chunk, 'error': str(e)})
                continue
        logger.info('Итого: получено %s цен:, ошибок: %s', len(all_prices), len(failed_chunks))
        return {ticker_id: Decimal(price_info['usd']) for ticker_id, price_info in all_prices.items()}
