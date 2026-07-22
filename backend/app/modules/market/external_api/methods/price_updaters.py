from collections.abc import Awaitable, Callable
import logging

from app.modules.market.models import Ticker
from app.modules.market.repositories import TickerRepository
from app.modules.market.services.ticker import TickerService
from app.modules.market.services.ticker_external_id import TickerExternalIdService

from .base import MethodBase

logger = logging.getLogger(__name__)


class BasePriceUpdater(MethodBase):
    NAME = 'Обновление цен'
    DESCRIPTION = 'Обновление цен тикеров'

    async def _save_prices(self, market: str, prices: dict, session) -> int:
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
        'top': '_fetch_top_coins',
        'active': '_fetch_active_coins',
        'all': '_fetch_all_coins',
        'used': '_fetch_used_coins',
    }

    async def run(self, market: str, get_prices: Callable[[list[str]], Awaitable[dict]], strategy: str = 'used', limit: int | None = None, *, provider_name: str, session=None, **_) -> dict:
        logger.info('Старт обновления цен со стратегией: %s', strategy)
        ticker_ids = await self._fetch_ticker_ids(market, strategy, limit, session)
        if not ticker_ids:
            return {'status': 'error', 'message': 'Нет тикеров для обновления'}

        ext_id_service = TickerExternalIdService(session)
        ext_id_map = await ext_id_service.resolve_to_external(ticker_ids, provider_name)

        ext_ids = [ext_id_map[tid] for tid in ticker_ids if tid in ext_id_map]
        if not ext_ids:
            return {'status': 'error', 'message': f'Нет external_id для {provider_name}'}

        prices = await get_prices(ext_ids)
        prices = await ext_id_service.resolve_to_internal(provider_name, prices)

        updated_count = await self._save_prices(market, prices, session=session)
        return {'status': 'success', 'message': f'Обновлено {updated_count} цен'}

    async def _fetch_ticker_ids(self, market: str, strategy: str, limit: int | None, session) -> list[int]:
        if strategy not in self.STRATEGIES:
            logger.warning('Неизвестная стратегия "%s", возврат к "used"', strategy)
            strategy = 'used'
        method_name = self.STRATEGIES[strategy]
        return await getattr(self, method_name)(market, limit, session)

    async def _fetch_top_coins(self, market: str, limit: int | None = None, session=None) -> list[int]:
        repo = TickerRepository(session)
        tickers = await repo.get_all(
            Ticker.market == market,
            Ticker.market_cap_rank.isnot(None),
            order=[Ticker.market_cap_rank.asc()],
        )
        tickers = tickers[:limit] if limit else tickers
        return [t.id for t in tickers]

    async def _fetch_active_coins(self, market: str, limit: int | None = None, session=None) -> list[int]:
        repo = TickerRepository(session)
        tickers = await repo.get_all(Ticker.market == market, Ticker.is_active.is_(True))
        tickers = tickers[:limit] if limit else tickers
        return [t.id for t in tickers]

    async def _fetch_all_coins(self, market: str, limit: int | None = None, session=None) -> list[int]:
        repo = TickerRepository(session)
        tickers = await repo.get_all_by_market(market)
        tickers = tickers[:limit] if limit else tickers
        return [t.id for t in tickers]

    async def _fetch_used_coins(self, market: str, limit: int | None = None, session=None) -> list[int]:
        from sqlalchemy import text

        query = text("""
            SELECT DISTINCT ticker_id FROM portfolio_asset
            UNION
            SELECT DISTINCT ticker_id FROM wallet_asset
        """)
        result = await session.execute(query)
        unique_ids = list(set(row[0] for row in result.all() if row[0]))
        logger.info('Получено %s уникальных используемых тикеров', len(unique_ids))
        return unique_ids[:limit] if limit else unique_ids


class FullPriceUpdater(BasePriceUpdater):
    PARAMETERS_SCHEMA: list[dict] = []

    async def run(self, market: str, fetch_prices: Callable[[], Awaitable[dict]], *, provider_name: str, session=None, **_) -> dict:
        prices = await fetch_prices()
        if not prices:
            return {'status': 'error', 'message': 'Нет данных от провайдера'}
        ext_id_service = TickerExternalIdService(session)
        prices = await ext_id_service.resolve_to_internal(provider_name, prices)
        updated_count = await self._save_prices(market, prices, session=session)
        return {'status': 'success', 'message': f'Обновлено {updated_count} цен'}


selective_price_updater = SelectivePriceUpdater()
full_price_updater = FullPriceUpdater()
