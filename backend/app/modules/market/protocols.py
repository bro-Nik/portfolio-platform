from typing import Protocol


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
