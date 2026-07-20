from decimal import Decimal
import logging

from ..core import BaseProvider, registry
from ..methods import smart_price_updater, ticker_loader
from ..url_chunker import chunk_ids_for_url

logger = logging.getLogger(__name__)


@registry.register_provider()
class CoingeckoProvider(BaseProvider):
    NAME = 'CoinGecko'
    DESCRIPTION = 'Криптовалютные данные и цены'
    BASE_URL = 'https://api.coingecko.com/api/v3'

    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_HOUR = 100
    REQUESTS_PER_DAY = 10000
    REQUESTS_PER_MONTH = 100000
    TIMEOUT = 30

    MAX_URL_LENGTH = 2048

    @registry.register_method(smart_price_updater)
    async def smart_price_update(self, **kwargs) -> dict:
        return await smart_price_updater.run('crypto', self.get_prices, **kwargs)

    @registry.register_method(ticker_loader)
    async def load_tickers(self, **kwargs) -> dict:
        return await ticker_loader.run('crypto', self.fetch_all_tickers, **kwargs)

    async def fetch_all_tickers(self) -> list[dict]:
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
            all_coins.extend(data)
            if len(data) < 250:
                break
            page += 1
        logger.info('Загружено %s монет с CoinGecko', len(all_coins))
        return all_coins

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
