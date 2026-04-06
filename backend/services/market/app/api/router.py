from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter

from shared.api import responses


class AppRouter(APIRouter):
    """APIRouter с DishkaRoute и стандартными responses."""

    def __init__(self, **kwargs) -> None:
        if 'responses' not in kwargs:
            kwargs['responses'] = responses(401, 429, 500)

        super().__init__(route_class=DishkaRoute, **kwargs)
