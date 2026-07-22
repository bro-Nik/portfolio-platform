from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.market.repositories import TickerExternalIdRepository


class TickerExternalIdService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TickerExternalIdRepository(session)

    async def resolve_to_external(self, ticker_ids: list[int], provider_name: str) -> dict[int, str]:
        return await self.repo.get_ext_id_map(ticker_ids, provider_name)

    async def resolve_to_internal(self, provider_name: str, ext_map: dict[str, object]) -> dict[int, object]:
        ext_ids = list(ext_map.keys())
        mapping = await self.repo.get_ticker_id_map(provider_name, ext_ids)
        return {mapping.get(k, k): v for k, v in ext_map.items()}

    async def get_ext_to_ticker_map(self, provider_name: str) -> dict[str, int]:
        return await self.repo.get_ext_to_ticker_map(provider_name)

    async def upsert(self, ticker_id: int, provider_name: str, ext_id: str) -> None:
        await self.repo.upsert(ticker_id, provider_name, ext_id)
