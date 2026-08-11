from collections.abc import AsyncIterator, Callable
import logging
from typing import TYPE_CHECKING

from .base import MethodBase

if TYPE_CHECKING:
    from app.modules.market.services.ticker import TickerService

logger = logging.getLogger(__name__)


class TickerLoader(MethodBase):
    """Синхронизация тикеров провайдера.

    Контракт: fetch_all_tickers() -> AsyncIterator[list[dict]] — пачки сырых записей.
    Обязательное поле записи: 'id' (внешний идентификатор тикера).
    Стратегии: 'all' — синхронизировать все тикеры, 'new' — только новые.
    """

    NAME = 'Загрузка тикеров'
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

    async def run(
        self,
        market: str,
        fetch_all_tickers: Callable,
        strategy: str = 'all',
        *,
        provider_name: str,
        ticker_service: 'TickerService',
        extract_identifiers: Callable[[dict], dict[str, str]] | None = None,
        **_,
    ) -> dict:
        logger.info('Старт загрузки тикеров, стратегия: %s', strategy)
        if strategy not in self.STRATEGIES:
            logger.warning('Неизвестная стратегия "%s", возврат к "all"', strategy)
            strategy = 'all'
        raw_data = fetch_all_tickers()
        method_name = self.STRATEGIES[strategy]
        return await getattr(self, method_name)(
            market,
            raw_data,
            provider_name=provider_name,
            extract_identifiers=extract_identifiers,
            ticker_service=ticker_service,
        )

    async def _sync_all(
        self,
        market: str,
        raw_data: AsyncIterator[list[dict]],
        provider_name: str,
        ticker_service: 'TickerService',
        extract_identifiers: Callable[[dict], dict[str, str]] | None = None,
    ) -> dict:
        return await ticker_service.sync_tickers(
            market,
            raw_data,
            strategy='all',
            provider_name=provider_name,
            extract_identifiers=extract_identifiers,
        )

    async def _sync_new(
        self,
        market: str,
        raw_data: AsyncIterator[list[dict]],
        provider_name: str,
        ticker_service: 'TickerService',
        extract_identifiers: Callable[[dict], dict[str, str]] | None = None,
    ) -> dict:
        return await ticker_service.sync_tickers(
            market,
            raw_data,
            strategy='new',
            provider_name=provider_name,
            extract_identifiers=extract_identifiers,
        )


ticker_loader = TickerLoader()
