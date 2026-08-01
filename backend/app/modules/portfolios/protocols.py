from typing import Any, Protocol


class TickerReader(Protocol):
    async def get_all_by_ids(self, ids: list[int]) -> list[Any]: ...


class TagReader(Protocol):
    async def get_tags(self, entity_type: str, entity_id: int) -> list[Any]: ...

    async def bulk_get_tags(self, items: list[tuple[str, int]]) -> dict[tuple[str, int], list[Any]]: ...
