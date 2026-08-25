from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter


class DishkaRouter(APIRouter):
    """APIRouter, чьи эндпоинты поддерживают внедрение зависимостей через Dishka (FromDishka)."""

    def __init__(self, **kwargs) -> None:
        super().__init__(route_class=DishkaRoute, **kwargs)
