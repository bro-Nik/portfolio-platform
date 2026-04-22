import logging

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.models import Ticker
from app.repositories import TickerRepository

logger = logging.getLogger(__name__)

BASE_IMAGES_URL = '/market/static/images/tickers'


class MarketTickerPrefix:
    CRYPTO = 'cr-'
    STOCK = 'st-'
    CURRENCY = 'cu-'

    @classmethod
    def add(cls, prefix: str, id: str) -> str:
        """Добавить префикс к ID тикера."""
        return id if id.startswith(prefix) else f'{prefix}{id}'

    @classmethod
    def remove(cls, prefix: str, id: str) -> str:
        """Убрать префикс у ID тикера."""
        return id if not id.startswith(prefix) else id.removeprefix(prefix)

    @classmethod
    def add_dict(cls, market: str, data: dict) -> dict:
        """Добавить префиксы ко всем ключам словаря."""
        prefix = getattr(cls, market.upper())
        return {cls.add(prefix, id): value for id, value in data.items()}

    @classmethod
    def remove_list(cls, market: str, data: list) -> list:
        """Убрать префиксы из всех ID списка."""
        prefix = getattr(cls, market.upper())
        return [cls.remove(prefix, id) for id in data]


class TickerService:
    """Сервис тикеров."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TickerRepository(session)

    async def search(
        self,
        search: str | None = None,
        market: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """Поиск тикеров с пагинацией."""
        # Базовые запросы
        query = select(models.Ticker)
        count_query = select(func.count()).select_from(models.Ticker)

        # Собираем условия
        where_conditions = []

        if search:
            search_term = f'%{search}%'
            where_conditions.append(
                or_(
                    models.Ticker.name.ilike(search_term),
                    models.Ticker.symbol.ilike(search_term),
                ),
            )

        if market:
            where_conditions.append(models.Ticker.market == market)

        if where_conditions:
            query = query.where(*where_conditions)
            count_query = count_query.where(*where_conditions)

        # Получаем общее количество
        total_count_result = await self.session.execute(count_query)
        total_count = total_count_result.scalar_one()

        # Пагинация
        offset = (page - 1) * page_size
        query = query.order_by(
            models.Ticker.market_cap_rank.asc().nulls_last(),
            models.Ticker.symbol.asc(),
        ).offset(offset).limit(page_size + 1)

        result = await self.session.execute(query)
        tickers = result.scalars().all()

        has_more = len(tickers) > page_size
        if has_more:
            tickers = tickers[:-1]

        return {
            'data': tickers,
            'has_more': has_more,
            'total': total_count,
        }

    async def get_prices(self, ids: list[str]) -> dict[str, float]:
        """Получить цены для списка тикеров."""
        tickers = await self.get_all(ids)
        return {ticker.id: ticker.price for ticker in tickers}

    async def get_images(self, ids: list[str]) -> dict[str, str]:
        """Получить URL изображений для списка тикеров."""
        tickers = await self.get_all(ids)
        return {
            t.id: f'{BASE_IMAGES_URL}/{t.market}/24/{t.image}'
            for t in tickers if t.image
        }

    async def get_info(self, ids: list[str]) -> dict[str, dict]:
        """Получить информацию о тикерах."""
        tickers = await self.get_all(ids)

        info = {}
        for ticker in tickers:
            info[ticker.id] = {
                'name': ticker.name,
                'symbol': ticker.symbol,
                'image': f'{BASE_IMAGES_URL}/{ticker.market}/24/{ticker.image}' if ticker.image else None,
            }
        return info

    async def get_all(self, ids: list) -> list[Ticker]:
        """Получить список тикеров."""
        return await self.repo.get_all_by_ids(ids)

    async def save_prices(self, market: str, price_data: dict) -> int:
        """Сохраняет цены."""
        # Добавляем префиксы
        data = MarketTickerPrefix.add_dict(market, price_data)

        batch_size: int = 500
        updated_total = 0
        ticker_ids = list(data.keys())

        # Обрабатываем батчами
        for i in range(0, len(ticker_ids), batch_size):
            batch_ids = ticker_ids[i:i + batch_size]
            batch_data = {id: data[id] for id in batch_ids}

            result = await self.repo.update_ticker_prices(batch_data)
            updated_total += result

        return updated_total
