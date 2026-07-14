from collections.abc import Callable
import logging

import httpx

from .base import MethodBase

logger = logging.getLogger(__name__)


class SmartPriceUpdater(MethodBase):
    NAME = 'Умное обновление цен'
    DESCRIPTION = 'Умное обновление цен с различными стратегиями'
    EXEMPLE_PARAMS = {'strategy': 'used', 'limit': 100}

    STRATEGIES = {
        'top': '_fetch_top_coins', 'active': '_fetch_active_coins',
        'all': '_fetch_all_coins', 'used': '_fetch_used_coins', 'auto': '_fetch_smart_coins',
    }

    async def run(self, market: str, get_prices: Callable, strategy: str = 'used', limit: int | None = None, **_) -> dict:
        logger.info('Старт умного обновления цен со стратегией: %s', strategy)
        ticker_ids = await self._fetch_ticker_ids(market, strategy, limit)
        if not ticker_ids:
            return {'status': 'error', 'message': 'Нет тикеров для обновления'}
        prices = await get_prices(ticker_ids)
        updated_count = await self._save_prices(market, prices)
        return {'status': 'success', 'message': f'Обновлено {updated_count} цен'}

    async def _save_prices(self, market: str, prices: dict) -> int:
        from app.core.database import AsyncSessionLocal
        from app.modules.market.services.ticker import TickerService
        async with AsyncSessionLocal() as session:
            ticker_service = TickerService(session)
            updated = await ticker_service.save_prices(market, prices)
            await session.commit()
            return updated

    async def _fetch_ticker_ids(self, market: str, strategy: str, limit: int | None) -> list[str]:
        if strategy not in self.STRATEGIES:
            logger.warning('Неизвестная стратегия "%s", возврат к "used"', strategy)
            strategy = 'used'
        method_name = self.STRATEGIES[strategy]
        return await getattr(self, method_name)(market, limit)

    async def _fetch_top_coins(self, market: str, limit: int | None = None) -> list[str]:
        return []
    async def _fetch_active_coins(self, market: str, limit: int | None = None) -> list[str]:
        return []
    async def _fetch_all_coins(self, market: str, limit: int | None = None) -> list[str]:
        return []
    async def _fetch_smart_coins(self, market: str, limit: int | None = None) -> list[str]:
        return []

    async def _fetch_used_coins(self, market: str, limit: int | None = None) -> list[str]:
        url = 'http://backend:8000/api/internal/all_used_tickers'
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
        unique_ids = list(set(data))
        logger.info('Получено %s уникальных используемых тикеров', len(unique_ids))
        return unique_ids[:limit] if limit else unique_ids


smart_price_updater = SmartPriceUpdater()
