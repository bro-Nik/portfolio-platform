from typing import Protocol


class EntityOwnershipChecker(Protocol):
    """Порт проверки владения сущностью, к которой прикрепляется тег.

    Реализуется модулем portfolios: tags не знает о его таблицах.
    """

    async def owns_entity(self, entity_type: str, entity_id: int, user_id: int) -> bool:
        """Принадлежит ли сущность указанному пользователю."""
        ...
