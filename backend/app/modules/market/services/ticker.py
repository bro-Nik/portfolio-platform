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
from app.modules.market.services.ticker_external_id import TickerExternalIdService
from app.modules.market.services.ticker_identifier import TickerIdentifierService

logger = logging.getLogger(__name__)

COUNTER_PERIODS = ['minute', 'hour', 'day', 'month']
BASE_IMAGES_URL = '/market/static/images/tickers'

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / 'static'
TICKER_IMAGES_DIR = STATIC_DIR / 'images' / 'tickers'


class TickerService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TickerRepository(session)
        self._ext_id_service = TickerExternalIdService(session)
        self._identifier_service = TickerIdentifierService(session)

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

    async def get_prices(self, ids: list[int]) -> dict[int, float]:
        tickers = await self.get_all(ids)
        return {t.id: t.price for t in tickers}

    async def get_images(self, ids: list[int]) -> dict[int, str]:
        tickers = await self.get_all(ids)
        return {t.id: f'{BASE_IMAGES_URL}/{t.market}/24/{t.image}' for t in tickers if t.image}

    async def get_info(self, ids: list[int]) -> dict[int, dict]:
        tickers = await self.get_all(ids)
        return {t.id: {'name': t.name, 'symbol': t.symbol, 'image': f'{BASE_IMAGES_URL}/{t.market}/24/{t.image}' if t.image else None} for t in tickers}

    async def get_all(self, ids: list) -> list[Ticker]:
        return await self.repo.get_all_by_ids(ids)

    async def get_all_by_market(self, market: str) -> list[Ticker]:
        return await self.repo.get_all_by_market(market)

    async def get_tickers_without_images(self, market: str) -> list[Ticker]:
        return await self.repo.get_all_by_market_without_images(market)

    async def sync_tickers(self, market: str, raw_data: list[dict], strategy: str = 'all', *,
                           provider_name: str,
                           extract_identifiers: Callable[[dict], dict[str, str]] | None = None) -> dict:
        ext_id_service = self._ext_id_service
        identifier_service = self._identifier_service

        ext_id_map = await ext_id_service.get_ext_to_ticker_map(provider_name)
        ticker_ids = list(ext_id_map.values())
        existing_tickers = await self.repo.get_all_by_ids(ticker_ids) if ticker_ids else []
        ticker_map = {t.id: t for t in existing_tickers}
        existing_by_ext = {ext_id: ticker_map[tid] for ext_id, tid in ext_id_map.items() if tid in ticker_map}

        created = 0
        updated = 0
        skipped = 0
        matched = 0

        for coin in raw_data:
            ext_id = coin.get('id')
            if not ext_id:
                continue

            ticker = existing_by_ext.get(ext_id)

            if not ticker and extract_identifiers:
                identifiers = extract_identifiers(coin)
                if identifiers:
                    matched_id = await identifier_service.find_matching_ticker(identifiers, market)
                    if matched_id:
                        ticker = ticker_map.get(matched_id)
                        if not ticker:
                            fetched = await self.repo.get_all_by_ids([matched_id])
                            if fetched:
                                ticker = fetched[0]
                                ticker_map[ticker.id] = ticker
                        if ticker:
                            existing_by_ext[ext_id] = ticker
                            matched += 1

            if ticker:
                if strategy == 'all':
                    self._update_ticker_fields(ticker, coin)
                    if not ticker.image:
                        image_url = coin.get('image')
                        if image_url:
                            image_file = await self._download_resize_image(image_url, market, ticker.id)
                            if image_file:
                                ticker.image = image_file
                    updated += 1
                else:
                    skipped += 1
            else:
                ticker = await self.repo.create({
                    'market': market,
                    'name': coin.get('name', ''),
                    'symbol': coin.get('symbol', ''),
                    'market_cap_rank': coin.get('market_cap_rank'),
                })
                image_url = coin.get('image')
                if image_url:
                    ticker.image = await self._download_resize_image(image_url, market, ticker.id)
                existing_by_ext[ext_id] = ticker
                created += 1

            await ext_id_service.upsert(ticker.id, provider_name, ext_id)
            if extract_identifiers:
                identifiers = extract_identifiers(coin)
                if identifiers:
                    await identifier_service.save_identifiers(ticker.id, identifiers)

        await self.session.flush()
        logger.info('sync_tickers(%s, %s): created=%s, updated=%s, skipped=%s, matched=%s',
                     market, strategy, created, updated, skipped, matched)
        return {'created': created, 'updated': updated, 'skipped': skipped, 'matched': matched}

    def _update_ticker_fields(self, ticker: Ticker, coin: dict) -> None:
        ticker.name = coin.get('name', ticker.name)
        ticker.symbol = coin.get('symbol', ticker.symbol)
        ticker.market_cap_rank = coin.get('market_cap_rank', ticker.market_cap_rank)

    async def _download_resize_image(self, image_url: str, market: str, ticker_id: int) -> str | None:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(image_url)
                response.raise_for_status()

            img = Image.open(BytesIO(response.content))
            ext = img.format.lower() if img.format else 'png'
            filename = f'{ticker_id}.{ext}'

            base_dir = TICKER_IMAGES_DIR / market

            for px in (24, 40):
                dir_path = base_dir / str(px)
                dir_path.mkdir(parents=True, exist_ok=True)
                img.resize((px, px), Image.LANCZOS).save(dir_path / filename)

            logger.info('Загружена иконка %s/%s', market, filename)
            return filename
        except Exception:
            logger.exception('Ошибка загрузки изображения %s: %s', ticker_id, image_url)
            return None

    async def save_prices(self, market: str, price_data: dict, *, provider_name: str | None = None) -> int:
        batch_size = 500
        updated_total = 0
        ticker_ids = list(price_data.keys())
        for i in range(0, len(ticker_ids), batch_size):
            batch_ids = ticker_ids[i:i + batch_size]
            batch_data = {id: price_data[id] for id in batch_ids}
            updated_total += await self.repo.update_ticker_prices(batch_data, price_updated_by=provider_name)
        return updated_total

    async def load_images(self, market: str, fetch_images: Callable[[list[str]], Awaitable[dict[str, str]]], *, provider_name: str) -> int:
        tickers = await self.get_tickers_without_images(market)
        if not tickers:
            return 0

        ext_id_service = self._ext_id_service
        ticker_ids = [t.id for t in tickers]
        ext_id_map = await ext_id_service.resolve_to_external(ticker_ids, provider_name)
        ext_ids = list(ext_id_map.values())
        if not ext_ids:
            return 0

        ticker_by_ext_id = {ext_id_map[t.id]: t for t in tickers if t.id in ext_id_map}

        image_urls = await fetch_images(ext_ids)

        loaded = 0
        for ext_id, url in image_urls.items():
            ticker = ticker_by_ext_id.get(ext_id)
            if ticker and url:
                ticker.image = await self._download_resize_image(url, market, ticker.id)
                loaded += 1

        return loaded
