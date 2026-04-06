from collections.abc import Callable
import logging

import httpx

from app.external_api.methods.base import MethodBase
from app.services.ticker import MarketTickerPrefix

logger = logging.getLogger(__name__)

class SmartPriceUpdater(MethodBase):
    """Умное обновление цен."""

    NAME = 'Умное обновление цен'
    DESCRIPTION = """Умное обновление цен с различными стратегиями.

        Стратегии:
        - 'top': только топ-N монет по капитализации
        - 'active': только активно торгуемые монеты
        - 'all': все монеты
        - 'used': используемые пользователями монеты
        - 'auto': автоматический выбор стратегии
    """

    EXEMPLE_PARAMS = {
        'strategy': 'used',
        'limit': 100,
    }

    STRATEGIES = {
        'top': '_fetch_top_coins',
        'active': '_fetch_active_coins',
        'all': '_fetch_all_coins',
        'used': '_fetch_used_coins',
        'auto': '_fetch_smart_coins',
    }

    async def run(self, market: str, get_prices: Callable, strategy: str = 'used', limit: int | None = None, **_) -> dict:
        """Умное обновление цен с различными стратегиями."""
        logger.info('Старт умного обновления цен со стратегией: %s', strategy)

        ticker_ids = await self._fetch_ticker_ids(market, strategy, limit)

        if not ticker_ids:
            logger.warning('Не получено тикеров для стратегии: %s', strategy)
            return {'status': 'error', 'message': 'Нет тикеров для обновления'}

        prices = await get_prices(ticker_ids)

        updated_count = await self._save_prices(market, prices)
        return {'status': 'success', 'message': f'Обновлено {updated_count} цен'}

    async def _save_prices(self, market: str, prices: dict) -> int:
        """Сохранить цены в БД."""
        from app.core.db import SessionLocal
        from app.services.ticker import TickerService

        async with SessionLocal() as session:
            ticker_service = TickerService(session)
            updated = await ticker_service.save_prices(market, prices)
            await session.commit()
            return updated

    async def _fetch_ticker_ids(self, market: str, strategy: str, limit: int | None) -> list[str]:
        """Получить ID тикеров по стратегии."""
        if strategy not in self.STRATEGIES:
            logger.warning('Неизвестная стратегия "%s", возврат к "used"', strategy)
            strategy = 'used'

        method_name = self.STRATEGIES[strategy]
        fetch_method = getattr(self, method_name)
        ticker_ids = await fetch_method(market, limit)

        # Убираем префиксы
        return MarketTickerPrefix.remove_list(market, ticker_ids)

    async def _fetch_top_coins(self, market: str, limit: int | None = None) -> list[str]:
        ids = []
        return ids[:limit] if limit else ids

    async def _fetch_active_coins(self, market: str, limit: int | None = None) -> list[str]:
        ids = []
        return ids[:limit] if limit else ids

    async def _fetch_all_coins(self, market: str, limit: int | None = None) -> list[str]:
        ids = []
        return ids[:limit] if limit else ids

    async def _fetch_smart_coins(self, market: str, limit: int | None = None) -> list[str]:
        ids = []
        return ids[:limit] if limit else ids

    async def _fetch_used_coins(self, market: str, limit: int | None = None) -> list[str]:
        url = 'http://portfolios:8000/api/internal/all_used_tickers'

        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

        unique_ids = list(set(data))
        logger.info('Получено %s уникальных используемых тикеров', len(unique_ids))
        return unique_ids[:limit] if limit else unique_ids

smart_price_updater = SmartPriceUpdater()
