from collections.abc import Awaitable, Callable
from io import BytesIO
from pathlib import Path
import logging

import httpx
from PIL import Image
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.market import models
from app.modules.market.models import Ticker
from app.modules.market.repositories import TickerRepository

logger = logging.getLogger(__name__)

COUNTER_PERIODS = ['minute', 'hour', 'day', 'month']
BASE_IMAGES_URL = '/market/static/images/tickers'

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / 'static'
TICKER_IMAGES_DIR = STATIC_DIR / 'images' / 'tickers'


class MarketTickerPrefix:
    CRYPTO = 'cr-'
    STOCK = 'st-'
    STOCKS = 'st-'
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

    async def get_all_by_market(self, market: str) -> list[Ticker]:
        return await self.repo.get_all_by_market(market)

    async def get_tickers_without_images(self, market: str) -> list[Ticker]:
        return await self.repo.get_all_by_market_without_images(market)

    async def sync_tickers(self, market: str, raw_data: list[dict], strategy: str = 'all', *, provider_name: str) -> dict:
        from app.modules.market.services.ticker_external_id import TickerExternalIdService

        prefix = getattr(MarketTickerPrefix, market.upper())
        ext_id_service = TickerExternalIdService(self.session)
        ext_id_map = await ext_id_service.get_ext_to_ticker_map(provider_name)
        ticker_ids = list(ext_id_map.values())
        existing_tickers = await self.repo.get_all_by_ids(ticker_ids) if ticker_ids else []
        ticker_map = {t.id: t for t in existing_tickers}
        existing_by_ext = {ext_id: ticker_map[tid] for ext_id, tid in ext_id_map.items() if tid in ticker_map}

        created = 0
        updated = 0
        skipped = 0

        for coin in raw_data:
            ext_id = coin.get('id')
            if not ext_id:
                continue

            ticker = existing_by_ext.get(ext_id)

            if ticker:
                if strategy == 'all':
                    self._update_ticker_fields(ticker, coin)
                    if not ticker.image:
                        image_url = coin.get('image')
                        if image_url:
                            image_file = await self._download_resize_image(image_url, market, ext_id)
                            if image_file:
                                ticker.image = image_file
                    updated += 1
                else:
                    skipped += 1
            else:
                full_id = f'{prefix}{ext_id}'
                ticker = await self.repo.create({
                    'id': full_id,
                    'market': market,
                    'name': coin.get('name', ''),
                    'symbol': coin.get('symbol', ''),
                    'market_cap_rank': coin.get('market_cap_rank'),
                })
                image_url = coin.get('image')
                if image_url:
                    ticker.image = await self._download_resize_image(image_url, market, ext_id)
                existing_by_ext[ext_id] = ticker
                created += 1

            await ext_id_service.upsert(ticker.id, provider_name, ext_id)

        await self.session.flush()
        logger.info('sync_tickers(%s, %s): created=%s, updated=%s, skipped=%s',
                     market, strategy, created, updated, skipped)
        return {'created': created, 'updated': updated, 'skipped': skipped}

    def _update_ticker_fields(self, ticker: Ticker, coin: dict) -> None:
        ticker.name = coin.get('name', ticker.name)
        ticker.symbol = coin.get('symbol', ticker.symbol)
        ticker.market_cap_rank = coin.get('market_cap_rank', ticker.market_cap_rank)

    async def _download_resize_image(self, image_url: str, market: str, ext_id: str) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(image_url)
                response.raise_for_status()

            img = Image.open(BytesIO(response.content))
            ext = img.format.lower() if img.format else 'png'
            filename = f'{ext_id}.{ext}'

            base_dir = TICKER_IMAGES_DIR / market

            for px in (24, 40):
                dir_path = base_dir / str(px)
                dir_path.mkdir(parents=True, exist_ok=True)
                img.resize((px, px), Image.LANCZOS).save(dir_path / filename)

            logger.info('Загружена иконка %s/%s', market, ext_id)
            return filename
        except Exception:
            logger.exception('Ошибка загрузки изображения %s: %s', ext_id, image_url)
            return None

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

    async def load_images(self, market: str, fetch_images: Callable[[list[str]], Awaitable[dict[str, str]]]) -> int:
        tickers = await self.get_tickers_without_images(market)
        if not tickers:
            return 0

        prefix = getattr(MarketTickerPrefix, market.upper())
        ext_ids = [MarketTickerPrefix.remove(prefix, t.id) for t in tickers]
        ticker_map = {MarketTickerPrefix.remove(prefix, t.id): t for t in tickers}

        image_urls = await fetch_images(ext_ids)

        loaded = 0
        for ext_id, url in image_urls.items():
            ticker = ticker_map.get(ext_id)
            if ticker and url:
                ticker.image = await self._download_resize_image(url, market, ext_id)
                loaded += 1

        return loaded
