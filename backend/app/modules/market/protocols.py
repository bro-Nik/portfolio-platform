from typing import Any, Protocol


class TickerCatalogReader(Protocol):
    """Порт чтения каталога тикеров market.

    Реализуется TickerService: потребители (watchlist) не знают о его
    устройстве и мокают маленький интерфейс вместо целого сервиса.
    """

    async def get(self, ticker_id: int) -> Any | None:
        """Карточка тикера или None, если нет."""
        ...

    async def get_info(self, ids: list[int]) -> dict[int, Any]:
        """Имя/символ/картинка/рынок по списку id."""
        ...

    async def get_prices(self, ids: list[int]) -> dict[int, float]:
        """Актуальные цены USD по списку id."""
        ...

    async def get_price_by_symbol(self, market: str, symbol: str) -> float | None:
        """Цена по символу внутри рынка (для пересчёта валют алертов)."""
        ...


class TickerUsageReader(Protocol):
    """Порт доступа market к данным об использовании тикеров пользователями.

    Реализуется модуля portfolios: market не знает о его таблицах.
    """

    async def get_used_ticker_ids(self, market: str | None = None) -> list[int]:
        """Идентификаторы тикеров, используемых хотя бы в одном активе.

        `market` ограничивает выборку одним рынком: без него задача для stocks
        провайдера запрашивала бы внешние id крипты.
        """
        ...

    async def count_references(self, ticker_id: int) -> int:
        """Количество записей пользователей, ссылающихся на тикер."""
        ...

    async def reassign_references(self, source_id: int, target_id: int) -> None:
        """Переназначить все ссылки с source-тикера на target-тикер."""
        ...


class PriceUpdateObserver(Protocol):
    """Порт уведомлений об обновлении цен.

    Реализуется модулем watchlist (проверка ценовых алертов): market не знает
    о его таблицах. Вызывается после коммита новых цен, ошибки наблюдателя
    не должны ронять задачу обновления — вызов обёрнут в try/except.
    """

    async def on_prices_updated(self, prices: dict[int, float]) -> None:
        """Проверить алерты по только что обновлённым ценам {ticker_id: price}."""
        ...
