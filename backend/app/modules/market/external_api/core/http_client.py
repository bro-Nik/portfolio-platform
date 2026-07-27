import asyncio
import logging
import time
from typing import Any

import httpx

from .rate_limiter import RateLimiter
from .request_logger import RequestLogger

logger = logging.getLogger(__name__)


class HTTPClient:
    TIMEOUT = 30.0
    MAX_CONNECTIONS = 100
    MAX_KEEPALIVE_CONNECTIONS = 20
    MAX_RETRIES = 3
    RETRY_BACKOFF = 1.0
    MAX_BACKOFF = 30.0

    def __init__(self, base_url: str, limiter: RateLimiter, logger: RequestLogger) -> None:
        self.base_url = base_url
        self.limiter = limiter
        self.logger = logger
        self.client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None or self.client.is_closed:
            limits = httpx.Limits(
                max_connections=self.MAX_CONNECTIONS,
                max_keepalive_connections=self.MAX_KEEPALIVE_CONNECTIONS,
                keepalive_expiry=30.0,
            )
            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.TIMEOUT),
                limits=limits,
                headers={'User-Agent': 'Crypto-Tracker/1.0', 'Accept': 'application/json'},
            )
        return self.client

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> float:
        retry_after = response.headers.get('Retry-After')
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                pass
        return 5.0

    async def request(
        self, method: str = 'GET', endpoint: str = '',
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        start_time = time.time()
        response = None
        client = await self._get_client()
        if endpoint.startswith('http://') or endpoint.startswith('https://'):
            url = endpoint
        else:
            url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        request_headers = {}
        if headers:
            request_headers.update(headers)

        async with self.limiter.limit():
            for attempt in range(self.MAX_RETRIES + 1):
                try:
                    logger.debug('Выполнить запрос к %s', url)
                    response = await client.request(
                        method=method.upper(), url=url,
                        params=params, data=data, json=json_data,
                        headers=request_headers, timeout=timeout or self.TIMEOUT,
                    )
                    await self.logger.log(method, endpoint, response, params, response_time=time.time() - start_time, url=url)
                    if not response.is_success:
                        response.raise_for_status()
                    return response.json()
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    await self.logger.log(method, endpoint, response, params, response_time=time.time() - start_time, error=str(e), url=url)
                    if attempt >= self.MAX_RETRIES:
                        logger.error('Ошибка запроса для %s: %s', url, e)
                        raise

                    if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 429:
                        retry_after = self._parse_retry_after(e.response)
                        logger.warning(
                            '429 Too Many Requests для %s, повтор через %.1fс (попытка %d/%d)',
                            url, retry_after, attempt + 1, self.MAX_RETRIES,
                        )
                        await asyncio.sleep(retry_after)
                    else:
                        backoff = min(self.RETRY_BACKOFF * (2 ** attempt), self.MAX_BACKOFF)
                        logger.warning(
                            'Ошибка соединения для %s, повтор через %.1fс (попытка %d/%d): %s',
                            url, backoff, attempt + 1, self.MAX_RETRIES, e,
                        )
                        await asyncio.sleep(backoff)

    async def close(self) -> None:
        if self.client and not self.client.is_closed:
            await self.client.aclose()
        await self.logger.save()
