from fastapi import APIRouter

from dishka.integrations.fastapi import DishkaRoute


class AppRouter(APIRouter):
    def __init__(self, **kwargs) -> None:
        super().__init__(route_class=DishkaRoute, **kwargs)
