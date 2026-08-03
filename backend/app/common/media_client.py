import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


class MediaClient:
    TIMEOUT = 30.0
    MAX_CONNECTIONS = 50
    MAX_KEEPALIVE = 10
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0
    MAX_BACKOFF = 30.0
    MAX_CONCURRENT = 10

    _shared_client: httpx.AsyncClient | None = None
    _semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    @classmethod
    def _get_client(cls) -> httpx.AsyncClient:
        if cls._shared_client is None or cls._shared_client.is_closed:
            limits = httpx.Limits(
                max_connections=cls.MAX_CONNECTIONS,
                max_keepalive_connections=cls.MAX_KEEPALIVE,
                keepalive_expiry=30.0,
            )
            cls._shared_client = httpx.AsyncClient(
                timeout=httpx.Timeout(cls.TIMEOUT),
                limits=limits,
                headers={'User-Agent': 'Crypto-Tracker/1.0'},
            )
        return cls._shared_client

    @classmethod
    async def download(cls, url: str) -> bytes:
        client = cls._get_client()
        async with cls._semaphore:
            for attempt in range(cls.MAX_RETRIES + 1):
                try:
                    response = await client.get(url)
                    response.raise_for_status()
                    return response.content
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        retry_after = float(e.response.headers.get('Retry-After', 5))
                        logger.warning(
                            '429 для %s, повтор через %.1fс (попытка %d/%d)',
                            url, retry_after, attempt + 1, cls.MAX_RETRIES,
                        )
                        await asyncio.sleep(retry_after)
                    else:
                        logger.exception('HTTP ошибка %s для %s', e.response.status_code, url)
                        raise
                except (httpx.ConnectTimeout, httpx.RequestError) as e:
                    if attempt >= cls.MAX_RETRIES:
                        logger.exception('Ошибка загрузки %s', url)
                        raise
                    backoff = min(cls.RETRY_BACKOFF * (2 ** attempt), cls.MAX_BACKOFF)
                    logger.warning(
                        'Повтор %s через %.1fс (попытка %d/%d): %s',
                        url, backoff, attempt + 1, cls.MAX_RETRIES, e,
                    )
                    await asyncio.sleep(backoff)

    @classmethod
    async def download_batch(cls, urls: list[str]) -> dict[str, bytes | Exception]:
        if not urls:
            return {}
        results = await asyncio.gather(
            *[cls.download(url) for url in urls],
            return_exceptions=True,
        )
        return dict(zip(urls, results))

    @classmethod
    async def close(cls) -> None:
        if cls._shared_client and not cls._shared_client.is_closed:
            await cls._shared_client.aclose()
            cls._shared_client = None
