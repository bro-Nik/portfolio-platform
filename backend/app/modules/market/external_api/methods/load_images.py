from collections.abc import Awaitable, Callable
import logging
from typing import TYPE_CHECKING

from .base import MethodBase

if TYPE_CHECKING:
    from app.modules.market.services.ticker import TickerService

logger = logging.getLogger(__name__)


class ImageLoader(MethodBase):
    """Загрузка изображений для тикеров без картинок.

    Контракт: fetch_images(ext_ids: list[str]) -> dict[str, str] —
    {внешний идентификатор: url изображения}.
    """

    NAME = 'Загрузка изображений'

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
