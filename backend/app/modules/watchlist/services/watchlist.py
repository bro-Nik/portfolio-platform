from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictError, NotFoundError
from app.common.schemas import Context
from app.modules.market.services.ticker import TickerService
from app.modules.watchlist.models import WatchlistItem
from app.modules.watchlist.repositories import WatchlistItemRepository


class WatchlistService:
    def __init__(self, session: AsyncSession, ctx: Context, ticker_service: TickerService) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.items = WatchlistItemRepository(session)
        self.tickers = ticker_service

    async def get_all(self) -> list[WatchlistItem]:
        items = await self.items.get_by_user(self.actor.id)
        await self._enrich(items)
        return items

    async def create(self, ticker_id: int, comment: str | None = None) -> WatchlistItem:
        ticker = await self.tickers.get(ticker_id)
        if not ticker:
            raise NotFoundError('Тикер не найден')
        if await self.items.exists_for_user(self.actor.id, ticker_id):
            raise ConflictError('Тикер уже в избранном')
        created = await self.items.create(
            {
                'ticker_id': ticker_id,
                'comment': comment,
                'user_id': self.actor.id,
            }
        )
        return await self._reload(created.id)

    async def update(self, item_id: int, comment: str | None) -> WatchlistItem:
        item = await self._get_own(item_id)
        await self.items.update(item.id, {'comment': comment})
        return await self._reload(item.id)

    async def archive(self, item_id: int, archived: bool) -> WatchlistItem:
        item = await self._get_own(item_id)
        await self.items.update(item.id, {'is_archived': archived})
        return await self._reload(item.id)

    async def delete(self, item_id: int) -> None:
        await self._get_own(item_id)
        await self.items.delete(item_id)

    async def _get_own(self, item_id: int) -> WatchlistItem:
        item = await self.items.get_own(item_id, self.actor.id)
        if not item:
            raise NotFoundError('Запись не найдена')
        return item

    async def _reload(self, item_id: int) -> WatchlistItem:
        """Перечитать с загруженными алертами: RETURNING после update связей не грузит."""
        item = await self._get_own(item_id)
        await self._enrich([item])
        return item

    async def _enrich(self, items: list[WatchlistItem]) -> None:
        """Проставляет тикерам имя/символ/картинку/рынок/цену из market-кеша."""
        if not items:
            return
        ticker_ids = list({i.ticker_id for i in items})
        info_map = await self.tickers.get_info(ticker_ids)
        prices = await self.tickers.get_prices(ticker_ids)
        for item in items:
            info = info_map.get(item.ticker_id)
            if info:
                item.name = info.name
                item.symbol = info.symbol
                item.image = info.image
                item.market = info.market
            item.price = prices.get(item.ticker_id)
