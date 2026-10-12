from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class ExportAccumulator:
    """Накопитель разделов выгрузки: модули дописывают сюда свои строки."""

    sections: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    ticker_ids: set[int] = field(default_factory=set)


class UserDataCollector(Protocol):
    """Порт раздела выгрузки персональных данных пользователя.

    Реализуется каждым модулем-владельцем таблиц: auth не знает о чужих моделях.
    Порядок вызова задаёт агрегат в app.di (portfolios раньше market —
    market читает собранные ticker_ids).
    """

    async def collect(self, user_id: int, acc: ExportAccumulator) -> None:
        """Добавить свой раздел в acc.sections (и ticker_ids при наличии)."""
        ...
