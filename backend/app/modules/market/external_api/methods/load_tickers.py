from collections.abc import Callable
import logging

from .base import MethodBase

logger = logging.getLogger(__name__)


class TickerLoader(MethodBase):
    NAME = 'Загрузка тикеров'
    DESCRIPTION = 'Загрузка и обновление списка доступных тикеров из API'
    EXEMPLE_PARAMS = {'strategy': 'all'}
    PARAMETERS_SCHEMA = [
        {
            'name': 'strategy',
            'label': 'Стратегия',
            'type': 'select',
            'options': {'all': 'Все тикеры', 'new': 'Только новые'},
            'default': 'all',
            'required': True,
        },
    ]

    STRATEGIES = {
        'all': '_sync_all',
        'new': '_sync_new',
    }

    async def run(self, market: str, fetch_all_tickers: Callable, strategy: str = 'all', **_) -> dict:
        logger.info('Старт загрузки тикеров, стратегия: %s', strategy)
        if strategy not in self.STRATEGIES:
            logger.warning('Неизвестная стратегия "%s", возврат к "all"', strategy)
            strategy = 'all'
        raw_tickers = await fetch_all_tickers()
        method_name = self.STRATEGIES[strategy]
        return await getattr(self, method_name)(market, raw_tickers)

    async def _sync_all(self, market: str, raw_tickers: list[dict]) -> dict:
        from app.core.database import AsyncSessionLocal
        from app.modules.market.services.ticker import TickerService
        async with AsyncSessionLocal() as session:
            ticker_service = TickerService(session)
            result = await ticker_service.sync_tickers(market, raw_tickers, strategy='all')
            await session.commit()
            return result

    async def _sync_new(self, market: str, raw_tickers: list[dict]) -> dict:
        from app.core.database import AsyncSessionLocal
        from app.modules.market.services.ticker import TickerService
        async with AsyncSessionLocal() as session:
            ticker_service = TickerService(session)
            result = await ticker_service.sync_tickers(market, raw_tickers, strategy='new')
            await session.commit()
            return result


ticker_loader = TickerLoader()
