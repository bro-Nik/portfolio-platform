from collections.abc import Awaitable, Callable
import logging

from app.modules.market.services.ticker import TickerService

from .base import MethodBase

logger = logging.getLogger(__name__)


class ImageLoader(MethodBase):
    NAME = 'Загрузка изображений'
    EXEMPLE_PARAMS = {}
    PARAMETERS_SCHEMA: list[dict] = []

    async def run(self, market: str, fetch_images: Callable[[list[str]], Awaitable[dict[str, str]]], *, provider_name: str, session=None, **_) -> dict:
        service = TickerService(session)
        loaded = await service.load_images(market, fetch_images, provider_name=provider_name)
        return {'loaded': loaded}


image_loader = ImageLoader()
