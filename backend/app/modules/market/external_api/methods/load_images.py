from collections.abc import Awaitable, Callable
import logging

from .base import MethodBase

logger = logging.getLogger(__name__)


class ImageLoader(MethodBase):
    NAME = 'Загрузка изображений'
    DESCRIPTION = 'Загрузка иконок/логотипов тикеров через API провайдера'
    EXEMPLE_PARAMS = {}
    PARAMETERS_SCHEMA: list[dict] = []

    async def run(self, market: str, fetch_images: Callable[[list[str]], Awaitable[dict[str, str]]], **_) -> dict:
        from app.core.database import AsyncSessionLocal
        from app.modules.market.services.ticker import TickerService

        async with AsyncSessionLocal() as session:
            service = TickerService(session)
            loaded = await service.load_images(market, fetch_images)
            await session.commit()
            return {'loaded': loaded}


image_loader = ImageLoader()
