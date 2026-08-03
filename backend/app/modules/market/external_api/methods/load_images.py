from collections.abc import Awaitable, Callable
import logging
from typing import TYPE_CHECKING

from .base import MethodBase

if TYPE_CHECKING:
    from app.modules.market.services.ticker import TickerService

logger = logging.getLogger(__name__)


class ImageLoader(MethodBase):
    NAME = 'Загрузка изображений'
    EXEMPLE_PARAMS = {}
    PARAMETERS_SCHEMA: list[dict] = []

    async def run(
        self,
        market: str,
        fetch_images: Callable[[list[str]], Awaitable[dict[str, str]]],
        *,
        provider_name: str,
        ticker_service: 'TickerService',
        **_,
    ) -> dict:
        loaded = await ticker_service.load_images(market, fetch_images, provider_name=provider_name)
        return {'loaded': loaded}


image_loader = ImageLoader()
