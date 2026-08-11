from collections.abc import AsyncIterator
import logging

from ..core import BaseProvider, registry
from ..methods import full_price_updater, ticker_loader

logger = logging.getLogger(__name__)

BOARD_PATH = 'engines/stock/markets/shares/boards/TQBR/securities.json'

SHARE_SECTYPES = ('1', '2')

SECURITIES_PARAMS = {
    'iss.meta': 'off',
    'iss.only': 'securities',
    'securities.columns': 'SECID,SHORTNAME,SECTYPE',
}

MARKETDATA_PARAMS = {
    'iss.meta': 'off',
    'iss.only': 'securities,marketdata',
    'securities.columns': 'SECID,SHORTNAME,SECTYPE',
    'marketdata.columns': 'SECID,LAST',
}


@registry.register_provider()
class MoexProvider(BaseProvider):
    NAME = 'Moex'
    DESCRIPTION = 'Акции РФ (Мосбиржа)'
    BASE_URL = 'https://iss.moex.com/iss/'
    API_KEY_REQUIRED = False

    REQUESTS_PER_MINUTE = 5
    REQUESTS_PER_HOUR = 30
    REQUESTS_PER_DAY = 100
    REQUESTS_PER_MONTH = 3000
    TIMEOUT = 30

    SUPPORTED_MARKETS = ['stocks']
    QUOTE_CURRENCY = 'RUB'

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

    async def _fetch_all_tickers(self) -> AsyncIterator[list[dict]]:
        try:
            data = await self.http.request('GET', BOARD_PATH, params=SECURITIES_PARAMS)
        except Exception:
            logger.exception('Ошибка загрузки тикеров Мосбиржи')
            return

        securities = data.get('securities', {})
        batch = [
            {'id': row['SECID'], 'symbol': row['SECID'], 'name': row['SHORTNAME']}
            for row in self._rows_to_dicts(securities)
            if row.get('SECTYPE') in SHARE_SECTYPES
        ]
        logger.info('Загружено %s тикеров акций РФ', len(batch))
        yield batch

    async def _fetch_all_prices(self) -> dict[str, float]:
        try:
            data = await self.http.request('GET', BOARD_PATH, params=MARKETDATA_PARAMS)
        except Exception:
            logger.exception('Ошибка загрузки цен Мосбиржи')
            return {}

        securities = self._rows_to_dicts(data.get('securities', {}))
        marketdata = self._rows_to_dicts(data.get('marketdata', {}))

        share_ids = {row['SECID'] for row in securities if row.get('SECTYPE') in SHARE_SECTYPES}
        prices_rub = {
            row['SECID']: row['LAST']
            for row in marketdata
            if row.get('SECID') in share_ids and row.get('LAST') is not None
        }
        if not prices_rub:
            logger.error('Нет цен акций РФ от Мосбиржи')
            return {}

        return prices_rub

    @staticmethod
    def _rows_to_dicts(block: dict) -> list[dict]:
        columns = block.get('columns', [])
        return [dict(zip(columns, row, strict=False)) for row in block.get('data', [])]
