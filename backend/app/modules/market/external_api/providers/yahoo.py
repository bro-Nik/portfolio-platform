from collections.abc import AsyncIterator
from decimal import Decimal
import logging

from ..core import BaseProvider, registry
from ..methods import selective_price_updater, ticker_loader

logger = logging.getLogger(__name__)

SPARK_SYMBOLS_PER_REQUEST = 20
SCREENER_PAGE_SIZE = 250

# Yahoo-символ: суффикс биржи -> валюта котировки
SUFFIX_CURRENCY = {
    '': 'USD', '.US': 'USD',
    '.DE': 'EUR', '.PA': 'EUR', '.MI': 'EUR', '.AS': 'EUR', '.BR': 'EUR',
    '.MC': 'EUR', '.VI': 'EUR', '.F': 'EUR', '.MU': 'EUR', '.SG': 'EUR',
    '.BE': 'EUR', '.DU': 'EUR', '.HM': 'EUR', '.HA': 'EUR', '.LS': 'EUR',
    '.IR': 'EUR', '.HE': 'EUR',
    '.L': 'GBP', '.IL': 'GBP',
    '.HK': 'HKD',
    '.T': 'JPY', '.JP': 'JPY',
    '.SS': 'CNY', '.SZ': 'CNY', '.CN': 'CNY',
    '.AX': 'AUD', '.AU': 'AUD',
    '.TO': 'CAD', '.V': 'CAD', '.CA': 'CAD',
    '.SW': 'CHF', '.CH': 'CHF',
    '.ST': 'SEK', '.SE': 'SEK',
    '.OL': 'NOK', '.NO': 'NOK',
    '.CO': 'DKK', '.DK': 'DKK',
    '.TW': 'TWD',
    '.SI': 'SGD', '.SG2': 'SGD',
    '.NS': 'INR', '.BO': 'INR', '.IN': 'INR',
    '.KS': 'KRW', '.KQ': 'KRW',
}

# Валюта -> (пара на spark, направление конвертации в USD)
# multiply: price * rate (базовая валюта пары), divide: price / rate (котировка пары)
FX_TO_USD = {
    'USD': (None, None),
    'EUR': ('EURUSD=X', 'multiply'),
    'GBP': ('GBPUSD=X', 'multiply'),
    'AUD': ('AUDUSD=X', 'multiply'),
    'NZD': ('NZDUSD=X', 'multiply'),
    'JPY': ('USDJPY=X', 'divide'),
    'CNY': ('USDCNY=X', 'divide'),
    'HKD': ('USDHKD=X', 'divide'),
    'SGD': ('USDSGD=X', 'divide'),
    'CHF': ('USDCHF=X', 'divide'),
    'CAD': ('USDCAD=X', 'divide'),
    'SEK': ('USDSEK=X', 'divide'),
    'NOK': ('USDNOK=X', 'divide'),
    'DKK': ('USDDKK=X', 'divide'),
    'TWD': ('USDTWD=X', 'divide'),
    'INR': ('USDINR=X', 'divide'),
    'KRW': ('USDKRW=X', 'divide'),
}

US_SCREENER_IDS = [
    'most_actives',
    'day_gainers',
    'day_losers',
    'undervalued_growth_stocks',
    'aggressive_small_caps',
    'most_shorted_stocks',
    'overbought_stocks',
    'oversold_stocks',
]

REGIONS = ['US', 'DE', 'GB', 'FR', 'IT', 'AU', 'CA', 'CN', 'IN', 'SG', 'HK']


def _currency_of(symbol: str) -> str | None:
    suffix = '.' + symbol.rsplit('.', 1)[1] if '.' in symbol else ''
    return SUFFIX_CURRENCY.get(suffix)


@registry.register_provider()
class YahooProvider(BaseProvider):
    NAME = 'YahooFinance'
    DESCRIPTION = 'Акции (США, Европа, Азия)'
    BASE_URL = 'https://query1.finance.yahoo.com/'
    API_KEY_REQUIRED = False

    REQUESTS_PER_MINUTE = 10
    REQUESTS_PER_HOUR = 200
    REQUESTS_PER_DAY = 2000
    REQUESTS_PER_MONTH = 20000
    TIMEOUT = 30

    SUPPORTED_MARKETS = ['stocks']
    QUOTE_CURRENCY = 'USD'

    @registry.register_method(ticker_loader)
    async def load_tickers(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await ticker_loader.run(market, self._fetch_all_tickers, **kwargs)

    @registry.register_method(selective_price_updater)
    async def selective_price_update(self, **kwargs) -> dict:
        market = self._resolve_market(kwargs)
        return await selective_price_updater.run(market, self.get_prices, **kwargs)

    async def _fetch_all_tickers(self) -> AsyncIterator[list[dict]]:
        seen: set[str] = set()
        for region in REGIONS:
            screener_ids = US_SCREENER_IDS if region == 'US' else ['most_actives']
            for screener_id in screener_ids:
                async for batch in self._fetch_screener_pages(region, screener_id, seen):
                    yield batch

    async def _fetch_screener_pages(
        self,
        region: str,
        screener_id: str,
        seen: set[str],
    ) -> AsyncIterator[list[dict]]:
        start = 0
        while True:
            params: dict = {
                'count': SCREENER_PAGE_SIZE,
                'start': start,
                'scrIds': screener_id,
                'formatted': 'false',
            }
            if region != 'US':
                params['marketRegion'] = region
            try:
                data = await self.http.request(
                    'GET', 'v1/finance/screener/predefined/saved', params=params,
                )
            except Exception:
                logger.exception(
                    'Ошибка загрузки тикеров региона %s, скринер %s (start=%s)',
                    region, screener_id, start,
                )
                break

            quotes = self._extract_quotes(data)
            batch = []
            for item in quotes:
                symbol = item.get('symbol')
                name = item.get('shortName')
                if item.get('quoteType') != 'EQUITY' or not symbol or not name:
                    continue
                if symbol in seen:
                    continue
                seen.add(symbol)
                batch.append({'id': symbol, 'symbol': symbol, 'name': name.strip()})

            if batch:
                logger.info(
                    'Регион %s (%s): загружено %s тикеров, всего %s',
                    region, screener_id, len(batch), len(seen),
                )
                yield batch

            if len(quotes) < SCREENER_PAGE_SIZE:
                break
            start += SCREENER_PAGE_SIZE

    @staticmethod
    def _extract_quotes(data: dict) -> list[dict]:
        result = (data or {}).get('finance', {}).get('result') or []
        return result[0].get('quotes', []) if result else []

    async def get_prices(self, ext_ids: list[str]) -> dict[str, Decimal]:
        if not ext_ids:
            return {}

        chunks = [
            ext_ids[i : i + SPARK_SYMBOLS_PER_REQUEST]
            for i in range(0, len(ext_ids), SPARK_SYMBOLS_PER_REQUEST)
        ]

        all_data: dict[str, float] = {}
        for chunk in chunks:
            params = {'symbols': ','.join(chunk), 'range': '1d', 'interval': '1d'}
            try:
                data = await self.http.request('GET', 'v8/finance/spark', params=params)
            except Exception:
                logger.exception('Ошибка запроса цен для %s символов', len(chunk))
                continue
            all_data.update(self._parse_spark(data))

        rates = await self._fetch_fx_rates()

        prices: dict[str, Decimal] = {}
        for ext_id in ext_ids:
            raw = all_data.get(ext_id)
            if raw is None:
                continue
            currency = _currency_of(ext_id)
            usd_price = self._to_usd(raw, currency, rates)
            if usd_price is None:
                logger.warning(
                    'Пропуск %s: неизвестная валюта %s или нет курса', ext_id, currency,
                )
                continue
            prices[ext_id] = usd_price

        logger.info('Получено цен: %s из %s', len(prices), len(ext_ids))
        return prices

    async def _fetch_fx_rates(self) -> dict[str, Decimal]:
        pairs = [info[0] for info in FX_TO_USD.values() if info[0]]
        params = {'symbols': ','.join(pairs), 'range': '1d', 'interval': '1d'}
        try:
            data = await self.http.request('GET', 'v8/finance/spark', params=params)
        except Exception:
            logger.exception('Ошибка запроса валютных курсов')
            return {}
        return self._parse_spark(data)

    @staticmethod
    def _parse_spark(data: dict) -> dict[str, float]:
        result: dict[str, float] = {}
        for symbol, item in (data or {}).items():
            if not isinstance(item, dict):
                continue
            closes = [c for c in (item.get('close') or []) if c is not None]
            if closes:
                result[symbol] = float(closes[-1])
        return result

    def _to_usd(
        self,
        price: float,
        currency: str | None,
        rates: dict[str, float],
    ) -> Decimal | None:
        fx_pair, direction = FX_TO_USD.get(currency or '', (None, None))
        if currency != 'USD':
            if not fx_pair:
                return None
            rate = rates.get(fx_pair)
            if rate is None:
                return None
            usd = price * rate if direction == 'multiply' else price / rate
        else:
            usd = price
        return Decimal(str(usd))
