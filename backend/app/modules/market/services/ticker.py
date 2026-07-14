from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.market import models
from app.modules.market.models import Ticker
from app.modules.market.repositories import TickerRepository


COUNTER_PERIODS = ['minute', 'hour', 'day', 'month']
BASE_IMAGES_URL = '/market/static/images/tickers'


class MarketTickerPrefix:
    CRYPTO = 'cr-'
    STOCK = 'st-'
    CURRENCY = 'cu-'

    @classmethod
    def add(cls, prefix: str, id: str) -> str:
        return id if id.startswith(prefix) else f'{prefix}{id}'

    @classmethod
    def remove(cls, prefix: str, id: str) -> str:
        return id if not id.startswith(prefix) else id.removeprefix(prefix)

    @classmethod
    def add_dict(cls, market: str, data: dict) -> dict:
        prefix = getattr(cls, market.upper())
        return {cls.add(prefix, id): value for id, value in data.items()}

    @classmethod
    def remove_list(cls, market: str, data: list) -> list:
        prefix = getattr(cls, market.upper())
        return [cls.remove(prefix, id) for id in data]


class TickerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TickerRepository(session)

    async def search(self, search: str | None = None, market: str | None = None, page: int = 1, page_size: int = 20) -> dict:
        query = select(models.Ticker)
        count_query = select(func.count()).select_from(models.Ticker)
        where = []
        if search:
            term = f'%{search}%'
            where.append(or_(models.Ticker.name.ilike(term), models.Ticker.symbol.ilike(term)))
        if market:
            where.append(models.Ticker.market == market)
        if where:
            query = query.where(*where)
            count_query = count_query.where(*where)
        total = (await self.session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        query = query.order_by(models.Ticker.market_cap_rank.asc().nulls_last(), models.Ticker.symbol.asc()).offset(offset).limit(page_size + 1)
        tickers = (await self.session.execute(query)).scalars().all()
        has_more = len(tickers) > page_size
        if has_more:
            tickers = tickers[:-1]
        return {'data': tickers, 'has_more': has_more, 'total': total}

    async def get_prices(self, ids: list[str]) -> dict[str, float]:
        tickers = await self.get_all(ids)
        return {t.id: t.price for t in tickers}

    async def get_images(self, ids: list[str]) -> dict[str, str]:
        tickers = await self.get_all(ids)
        return {t.id: f'{BASE_IMAGES_URL}/{t.market}/24/{t.image}' for t in tickers if t.image}

    async def get_info(self, ids: list[str]) -> dict[str, dict]:
        tickers = await self.get_all(ids)
        return {t.id: {'name': t.name, 'symbol': t.symbol, 'image': f'{BASE_IMAGES_URL}/{t.market}/24/{t.image}' if t.image else None} for t in tickers}

    async def get_all(self, ids: list) -> list[Ticker]:
        return await self.repo.get_all_by_ids(ids)

    async def save_prices(self, market: str, price_data: dict) -> int:
        data = MarketTickerPrefix.add_dict(market, price_data)
        batch_size = 500
        updated_total = 0
        ticker_ids = list(data.keys())
        for i in range(0, len(ticker_ids), batch_size):
            batch_ids = ticker_ids[i:i + batch_size]
            batch_data = {id: data[id] for id in batch_ids}
            updated_total += await self.repo.update_ticker_prices(batch_data)
        return updated_total
