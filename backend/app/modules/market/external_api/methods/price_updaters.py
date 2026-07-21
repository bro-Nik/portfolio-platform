from collections.abc import Awaitable, Callable
import logging

import httpx

from .base import MethodBase

logger = logging.getLogger(__name__)


class BasePriceUpdater(MethodBase):
    NAME = 'Обновление цен'
    DESCRIPTION = 'Обновление цен тикеров'

    async def _save_prices(self, market: str, prices: dict, session) -> int:
        from app.modules.market.services.ticker import TickerService
        ticker_service = TickerService(session)
        return await ticker_service.save_prices(market, prices)


class SelectivePriceUpdater(BasePriceUpdater):
    PARAMETERS_SCHEMA = [
        {
            'name': 'strategy',
            'label': 'Стратегия',
            'type': 'select',
            'options': {
                'top': 'Топ монеты',
                'active': 'Активные',
                'all': 'Все монеты',
                'used': 'Используемые',
                'auto': 'Авто',
            },
            'default': 'used',
            'required': True,
        },
        {
            'name': 'limit',
            'label': 'Лимит тикеров',
            'type': 'number',
            'default': None,
            'required': False,
        },
    ]

    STRATEGIES = {
        'top': '_fetch_top_coins', 'active': '_fetch_active_coins',
        'all': '_fetch_all_coins', 'used': '_fetch_used_coins', 'auto': '_fetch_smart_coins',
    }

    async def run(self, market: str, get_prices: Callable[[list[str]], Awaitable[dict]], strategy: str = 'used', limit: int | None = None, *, provider_name: str, session=None, **_) -> dict:
        logger.info('Старт обновления цен со стратегией: %s', strategy)
        ticker_ids = await self._fetch_ticker_ids(market, strategy, limit)
        if not ticker_ids:
            return {'status': 'error', 'message': 'Нет тикеров для обновления'}

        from app.modules.market.services.ticker_external_id import TickerExternalIdService

        ext_id_service = TickerExternalIdService(session)
        ext_id_map = await ext_id_service.resolve_to_external(ticker_ids, provider_name)

        ext_ids = [ext_id_map[tid] for tid in ticker_ids if tid in ext_id_map]
        if not ext_ids:
            return {'status': 'error', 'message': f'Нет external_id для {provider_name}'}

        prices = await get_prices(ext_ids)
        prices = await ext_id_service.resolve_to_internal(provider_name, prices)

        updated_count = await self._save_prices(market, prices, session=session)
        return {'status': 'success', 'message': f'Обновлено {updated_count} цен'}

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


class FullPriceUpdater(BasePriceUpdater):
    PARAMETERS_SCHEMA: list[dict] = []

    async def run(self, market: str, fetch_prices: Callable[[], Awaitable[dict]], session=None, **_) -> dict:
        prices = await fetch_prices()
        if not prices:
            return {'status': 'error', 'message': 'Нет данных от провайдера'}
        updated_count = await self._save_prices(market, prices, session=session)
        return {'status': 'success', 'message': f'Обновлено {updated_count} цен'}


selective_price_updater = SelectivePriceUpdater()
full_price_updater = FullPriceUpdater()
