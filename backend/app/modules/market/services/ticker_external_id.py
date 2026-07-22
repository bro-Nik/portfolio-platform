import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.market.repositories import TickerExternalIdRepository

logger = logging.getLogger(__name__)


class TickerExternalIdService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TickerExternalIdRepository(session)

    async def resolve_to_external(self, ticker_ids: list[int], provider_name: str) -> dict[int, str]:
        return await self.repo.get_ext_id_map(ticker_ids, provider_name)

    async def resolve_to_internal(self, provider_name: str, ext_map: dict[str, object]) -> dict[int, object]:
        ext_ids = list(ext_map.keys())
        mapping = await self.repo.get_ticker_id_map(provider_name, ext_ids)
        result = {}
        for ext_id, value in ext_map.items():
            ticker_id = mapping.get(ext_id)
            if ticker_id is not None:
                result[ticker_id] = value
            else:
                logger.warning('resolve_to_internal(%s): external_id %s не найден, пропускаем', provider_name, ext_id)
        return result

    async def get_ext_to_ticker_map(self, provider_name: str) -> dict[str, int]:
        return await self.repo.get_ext_to_ticker_map(provider_name)

    async def upsert(self, ticker_id: int, provider_name: str, ext_id: str) -> None:
        await self.repo.upsert(ticker_id, provider_name, ext_id)
