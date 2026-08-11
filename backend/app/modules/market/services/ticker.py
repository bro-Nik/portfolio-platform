import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from io import BytesIO
import logging
from pathlib import Path

from PIL import Image
from redis.asyncio import Redis
from sqlalchemy import func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BusinessRuleError, NotFoundError
from app.common.media_client import MediaClient
from app.modules.market.models import Ticker, TickerExternalId, TickerIdentifier
from app.modules.market.repositories import TickerRepository
from app.modules.market.schemas import TickerDetailResponse, TickerInfo, TickerListResponse, TickerUpdateRequest
from app.modules.market.services.ticker_external_id import TickerExternalIdService
from app.modules.market.services.ticker_identifier import TickerIdentifierService

logger = logging.getLogger(__name__)

BASE_IMAGES_URL = '/market/static/images/tickers'

PRICE_CACHE_TTL = 15 * 60
INFO_CACHE_TTL = 60 * 60

STATIC_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent / 'static'
TICKER_IMAGES_DIR = STATIC_DIR / 'images' / 'tickers'


class TickerService:
    def __init__(
        self,
        session: AsyncSession,
        repo: TickerRepository,
        ext_id_service: TickerExternalIdService,
        identifier_service: TickerIdentifierService,
        redis: Redis | None = None,
    ) -> None:
        self.session = session
        self.repo = repo
        self._ext_id_service = ext_id_service
        self._identifier_service = identifier_service
        self._redis = redis

    async def search(
        self,
        search: str | None = None,
        markets: list[str] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        query = select(Ticker)
        count_query = select(func.count()).select_from(Ticker)
        where = []
        if search:
            term = f'%{search}%'
            where.append(or_(Ticker.name.ilike(term), Ticker.symbol.ilike(term)))
        if markets:
            where.append(Ticker.market.in_(markets))
        if where:
            query = query.where(*where)
            count_query = count_query.where(*where)
        total = (await self.session.execute(count_query)).scalar_one()
        offset = (page - 1) * page_size
        query = (
            query.order_by(Ticker.market_cap_rank.asc().nulls_last(), Ticker.symbol.asc())
            .offset(offset)
            .limit(page_size + 1)
        )
        tickers = (await self.session.execute(query)).scalars().all()
        has_more = len(tickers) > page_size
        if has_more:
            tickers = tickers[:-1]
        return {'data': tickers, 'has_more': has_more, 'total': total}

    async def get(self, ticker_id: int) -> TickerDetailResponse:
        ticker = await self.repo.get(ticker_id)
        if not ticker:
            raise NotFoundError('Тикер не найден')
        return TickerDetailResponse.model_validate(ticker)

    async def get_all_admin(
        self,
        search: str | None = None,
        markets: list[str] | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TickerListResponse:
        result = await self.search(search=search, markets=markets, page=page, page_size=page_size)
        return TickerListResponse(
            data=[TickerDetailResponse.model_validate(t) for t in result['data']],
            has_more=result['has_more'],
            total=result['total'],
        )

    async def get_all_by_market(self, market: str) -> list[Ticker]:
        return await self.repo.get_all_by_market(market)

    async def get_tickers_without_images(self, market: str) -> list[Ticker]:
        return await self.repo.get_all_by_market_without_images(market)

    async def get_prices(self, ids: list[int]) -> dict[int, float]:
        prices = await self._get_cached_prices(ids)
        missing = [id for id in ids if id not in prices]
        if missing:
            tickers = await self.repo.get_all_by_ids(missing)
            prices.update({t.id: t.price for t in tickers})
            await self._set_cached_prices({t.id: t.price for t in tickers})
        return prices

    async def get_images(self, ids: list[int]) -> dict[int, str]:
        info = await self.get_info(ids)
        return {id: item.image for id, item in info.items() if item.image}

    async def get_info(self, ids: list[int]) -> dict[int, TickerInfo]:
        info = await self._get_cached_infos(ids)
        missing = [id for id in ids if id not in info]
        if missing:
            tickers = await self.repo.get_all_by_ids(missing)
            for t in tickers:
                info[t.id] = self._info_dict(t)
            await self._set_cached_infos(tickers)
        return info

    async def sync_tickers(
        self,
        market: str,
        raw_data: AsyncIterator[list[dict]],
        strategy: str = 'all',
        *,
        provider_name: str,
        extract_identifiers: Callable[[dict], dict[str, str]] | None = None,
    ) -> dict:
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
        touched_ids: list[int] = []

        async for batch in raw_data:
            queued_images: list[tuple[str, Ticker]] = []

            for coin in batch:
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
                        image_url = coin.get('image') if not ticker.image else None
                        updated += 1
                        touched_ids.append(ticker.id)
                    else:
                        skipped += 1
                        continue
                else:
                    ticker = await self.repo.create({
                        'market': market,
                        'name': coin.get('name', ''),
                        'symbol': coin.get('symbol', ''),
                        'market_cap_rank': coin.get('market_cap_rank'),
                    })
                    await self.session.flush()
                    existing_by_ext[ext_id] = ticker
                    image_url = coin.get('image')
                    created += 1
                    touched_ids.append(ticker.id)

                await ext_id_service.upsert(ticker.id, provider_name, ext_id)
                if extract_identifiers:
                    identifiers = extract_identifiers(coin)
                    if identifiers:
                        await identifier_service.save_identifiers(ticker.id, identifiers)

                if image_url:
                    queued_images.append((image_url, ticker))

            if queued_images:
                urls = [url for url, _ in queued_images]
                results = await MediaClient.download_batch(urls)
                for url, ticker in queued_images:
                    content = results.get(url)
                    if isinstance(content, Exception):
                        continue
                    filename = await asyncio.to_thread(self._process_image, content, market, ticker.id)
                    if filename:
                        ticker.image = filename

            await self.session.flush()
            await self.session.commit()

        await self._invalidate_infos(touched_ids)

        logger.info('sync_tickers(%s, %s): created=%s, updated=%s, skipped=%s, matched=%s',
            market, strategy, created, updated, skipped, matched)
        return {'created': created, 'updated': updated, 'skipped': skipped, 'matched': matched}

    async def get_price_by_symbol(self, market: str, symbol: str) -> float | None:
        tickers = await self.repo.get_all_by_symbols(market, [symbol])
        return float(tickers[0].price) if tickers else None

    async def resolve_prices_by_symbol(self, market: str, prices: dict[str, object]) -> dict[int, object]:
        if not prices:
            return {}
        tickers = await self.repo.get_all_by_symbols(market, list(prices.keys()))
        by_symbol = {t.symbol: t.id for t in tickers}
        return {by_symbol[symbol]: value for symbol, value in prices.items() if symbol in by_symbol}

    async def save_prices(self, market: str, price_data: dict, *, provider_name: str | None = None) -> int:
        batch_size = 500
        updated_total = 0
        ticker_ids = list(price_data.keys())
        for i in range(0, len(ticker_ids), batch_size):
            batch_ids = ticker_ids[i : i + batch_size]
            batch_data = {id: price_data[id] for id in batch_ids}
            updated_total += await self.repo.update_ticker_prices(batch_data, price_updated_by=provider_name)
        await self.session.commit()
        await self._invalidate_prices(ticker_ids)
        return updated_total

    async def load_images(
        self,
        market: str,
        fetch_images: Callable[[list[str]], Awaitable[dict[str, str]]],
        *,
        provider_name: str,
    ) -> int:
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

        tasks = []
        for ext_id, url in image_urls.items():
            ticker = ticker_by_ext_id.get(ext_id)
            if ticker and url:
                tasks.append((ticker, url))

        if not tasks:
            return 0

        urls = [url for _, url in tasks]
        results = await MediaClient.download_batch(urls)

        loaded = 0
        loaded_ids: list[int] = []
        for ticker, url in tasks:
            content = results.get(url)
            if isinstance(content, Exception):
                continue
            filename = await asyncio.to_thread(self._process_image, content, market, ticker.id)
            if filename:
                ticker.image = filename
                loaded += 1
                loaded_ids.append(ticker.id)

        await self.session.commit()
        await self._invalidate_infos(loaded_ids)

        return loaded

    async def update(self, ticker_id: int, data: TickerUpdateRequest) -> TickerDetailResponse:
        ticker = await self.repo.get(ticker_id)
        if not ticker:
            raise NotFoundError('Тикер не найден')
        dump = data.model_dump(exclude_unset=True)
        if not dump:
            raise BusinessRuleError('Нет полей для обновления')
        updated = await self.repo.update(ticker_id, dump)
        await self.session.commit()
        await self._invalidate_infos([ticker_id])
        return TickerDetailResponse.model_validate(updated)

    async def delete(self, ticker_id: int) -> None:
        ticker = await self.repo.get(ticker_id)
        if not ticker:
            raise NotFoundError('Тикер не найден')

        refs = await self._count_references(ticker_id)
        if refs > 0:
            raise BusinessRuleError(f'Тикер используется в {refs} записях. Удалите или переназначьте их перед удалением.')

        if ticker.image:
            self._delete_image_files(ticker.image, ticker.market)

        await self.repo.delete(ticker_id)
        await self.session.commit()
        await self._invalidate_infos([ticker_id])
        await self._invalidate_prices([ticker_id])

    async def merge(self, source_id: int, target_id: int) -> TickerDetailResponse:
        if source_id == target_id:
            raise BusinessRuleError('Нельзя объединить тикер с самим собой')

        source = await self.repo.get(source_id)
        target = await self.repo.get(target_id)
        if not source or not target:
            raise NotFoundError('Один из тикеров не найден')

        await self._merge_handle_image(source, target)
        await self._merge_reassign_external_ids(source_id, target_id)
        await self._merge_reassign_identifiers(source_id, target_id)
        await self._merge_update_references(source_id, target_id)

        await self.repo.delete(source_id)
        await self.session.commit()

        merged_ids = [source_id, target_id]
        await self._invalidate_infos(merged_ids)
        await self._invalidate_prices(merged_ids)

        merged = await self.repo.get(target_id, relations=['external_ids', 'identifiers'])
        return TickerDetailResponse.model_validate(merged)

    @staticmethod
    def _info_dict(t: Ticker) -> TickerInfo:
        return TickerInfo(
            name=t.name,
            symbol=t.symbol,
            image=f'{BASE_IMAGES_URL}/{t.market}/24/{t.image}' if t.image else None,
            market=t.market,
        )

    def _update_ticker_fields(self, ticker: Ticker, coin: dict) -> None:
        ticker.name = coin.get('name', ticker.name)
        ticker.symbol = coin.get('symbol', ticker.symbol)
        ticker.market_cap_rank = coin.get('market_cap_rank', ticker.market_cap_rank)

    def _process_image(self, content: bytes, market: str, ticker_id: int) -> str | None:
        img = Image.open(BytesIO(content))
        ext = img.format.lower() if img.format else 'png'
        filename = f'{ticker_id}.{ext}'

        base_dir = TICKER_IMAGES_DIR / market

        for px in (24, 40):
            dir_path = base_dir / str(px)
            dir_path.mkdir(parents=True, exist_ok=True)
            img.resize((px, px), Image.LANCZOS).save(dir_path / filename)

        return filename

    async def _get_cached_prices(self, ids: list[int]) -> dict[int, float]:
        if not self._redis or not ids:
            return {}
        try:
            values = await self._redis.mget([self._price_key(id) for id in ids])
        except Exception:
            logger.warning('Не удалось прочитать цены тикеров из Redis, fallback на SQL', exc_info=True)
            return {}
        result = {}
        for id, v in zip(ids, values, strict=False):
            if v is None:
                continue
            try:
                result[id] = float(v)
            except ValueError:
                continue
        return result

    async def _set_cached_prices(self, prices: dict[int, float]) -> None:
        if not self._redis or not prices:
            return
        try:
            async with self._redis.pipeline(transaction=False) as pipe:
                for id, price in prices.items():
                    if price is None:
                        continue
                    pipe.set(self._price_key(id), str(price), ex=PRICE_CACHE_TTL)
                await pipe.execute()
        except Exception:
            logger.warning('Не удалось записать цены тикеров в Redis', exc_info=True)

    async def _get_cached_infos(self, ids: list[int]) -> dict[int, TickerInfo]:
        if not self._redis or not ids:
            return {}
        try:
            values = await self._redis.mget([self._info_key(id) for id in ids])
        except Exception:
            logger.warning('Не удалось прочитать инфо тикеров из Redis, fallback на SQL', exc_info=True)
            return {}
        result = {}
        for id, v in zip(ids, values, strict=False):
            if v is None:
                continue
            try:
                result[id] = TickerInfo.model_validate_json(v)
            except ValueError:
                continue
        return result

    async def _set_cached_infos(self, tickers: list[Ticker]) -> None:
        if not self._redis or not tickers:
            return
        try:
            async with self._redis.pipeline(transaction=False) as pipe:
                for t in tickers:
                    pipe.set(self._info_key(t.id), self._info_dict(t).model_dump_json(), ex=INFO_CACHE_TTL)
                await pipe.execute()
        except Exception:
            logger.warning('Не удалось записать инфо тикеров в Redis', exc_info=True)

    async def _invalidate_prices(self, ids: list[int]) -> None:
        await self._delete_keys([self._price_key(id) for id in ids])

    async def _invalidate_infos(self, ids: list[int]) -> None:
        await self._delete_keys([self._info_key(id) for id in ids])

    async def _delete_keys(self, keys: list[str]) -> None:
        if not self._redis or not keys:
            return
        try:
            await self._redis.delete(*keys)
        except Exception:
            logger.warning('Не удалось удалить ключи тикеров из Redis', exc_info=True)

    def _price_key(self, ticker_id: int) -> str:
        return f'ticker:price:{ticker_id}'

    def _info_key(self, ticker_id: int) -> str:
        return f'ticker:info:{ticker_id}'

    async def _count_references(self, ticker_id: int) -> int:
        result = await self.session.execute(
            text("""
            SELECT
                (SELECT COUNT(*) FROM portfolio_asset WHERE ticker_id = :id) +
                (SELECT COUNT(*) FROM wallet_asset WHERE ticker_id = :id) +
                (SELECT COUNT(*) FROM "transaction" WHERE ticker_id = :id) +
                (SELECT COUNT(*) FROM "transaction" WHERE ticker2_id = :id)
        """),
            {'id': ticker_id},
        )
        return result.scalar() or 0

    def _delete_image_files(self, filename: str, market: str) -> None:
        for px in (24, 40):
            path = TICKER_IMAGES_DIR / market / str(px) / filename
            path.unlink(missing_ok=True)

    async def _merge_update_references(self, source_id: int, target_id: int) -> None:
        tables = [
            ('portfolio_asset', 'ticker_id'),
            ('wallet_asset', 'ticker_id'),
            ('"transaction"', 'ticker_id'),
            ('"transaction"', 'ticker2_id'),
        ]
        for table, column in tables:
            await self.session.execute(
                text(f'UPDATE {table} SET {column} = :target WHERE {column} = :source'),
                {'source': source_id, 'target': target_id},
            )

    async def _merge_handle_image(self, source: Ticker, target: Ticker) -> None:
        if not source.image:
            return
        ext = source.image.rsplit('.', 1)[-1]
        for px in (24, 40):
            src = TICKER_IMAGES_DIR / source.market / str(px) / source.image
            if not src.exists():
                continue
            if target.image:
                src.unlink(missing_ok=True)
            else:
                dst = TICKER_IMAGES_DIR / target.market / str(px) / f'{target.id}.{ext}'
                dst.parent.mkdir(parents=True, exist_ok=True)
                src.rename(dst)
        if not target.image:
            target.image = f'{target.id}.{ext}'

    async def _merge_reassign_external_ids(self, source_id: int, target_id: int) -> None:
        existing = await self.session.execute(
            select(TickerExternalId.provider_name).where(TickerExternalId.ticker_id == target_id)
        )
        target_providers = {row[0] for row in existing}

        rows = await self.session.execute(select(TickerExternalId).where(TickerExternalId.ticker_id == source_id))
        for row in rows.scalars():
            if row.provider_name not in target_providers:
                row.ticker_id = target_id
            else:
                await self.session.delete(row)

    async def _merge_reassign_identifiers(self, source_id: int, target_id: int) -> None:
        existing = await self.session.execute(
            select(TickerIdentifier.system, TickerIdentifier.value).where(TickerIdentifier.ticker_id == target_id)
        )
        target_keys = {(row.system, row.value) for row in existing}

        rows = await self.session.execute(select(TickerIdentifier).where(TickerIdentifier.ticker_id == source_id))
        for row in rows.scalars():
            key = (row.system, row.value)
            if key not in target_keys:
                row.ticker_id = target_id
            else:
                await self.session.delete(row)
