import logging
import time
from typing import Any

import httpx

from .rate_limiter import RateLimiter
from .request_logger import RequestLogger, _sanitize_url, sanitize_error
from app.common.utils.retry import parse_retry_after, retry_pause
from app.modules.market.external_api.exceptions import ExternalAPIError

logger = logging.getLogger(__name__)

# 503 — второй по частоте статус, который приходит с Retry-After.
RETRY_AFTER_STATUSES = frozenset({429, 503})


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
        return parse_retry_after(response)

    @staticmethod
    def _is_retryable(error: httpx.HTTPStatusError | httpx.RequestError) -> bool:
        if isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code
            return status == 429 or status >= 500
        return True

    async def request(
        self,
        method: str = 'GET',
        endpoint: str = '',
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
    ) -> dict[str, Any]:
        response = None
        client = await self._get_client()
        if endpoint.startswith(('http://', 'https://')):
            url = endpoint
        else:
            url = f'{self.base_url.rstrip("/")}/{endpoint.lstrip("/")}'
        safe_url = _sanitize_url(url)

        request_headers = {}
        if headers:
            request_headers.update(headers)

        async with self.limiter.limit():
            for attempt in range(self.MAX_RETRIES + 1):
                # Замер на попытку, а не от начала запроса: иначе avg_response_time
                # в админке включал бы все backoff-паузы между попытками.
                attempt_started = time.time()
                try:
                    logger.debug('Выполнить запрос к %s', safe_url)
                    response = await client.request(
                        method=method.upper(),
                        url=url,
                        params=params,
                        data=data,
                        json=json_data,
                        headers=request_headers,
                        timeout=timeout or self.TIMEOUT,
                    )
                except (httpx.HTTPStatusError, httpx.RequestError) as e:
                    error = sanitize_error(str(e))
                    await self.logger.log(
                        method,
                        endpoint,
                        response,
                        params,
                        response_time=time.time() - attempt_started,
                        error=error,
                        url=url,
                    )
                    if not self._is_retryable(e) or attempt >= self.MAX_RETRIES:
                        logger.exception('Ошибка запроса для %s: %s', safe_url, error)
                        raise

                    retry_after = (
                        self._parse_retry_after(e.response)
                        if isinstance(e, httpx.HTTPStatusError) and e.response.status_code in RETRY_AFTER_STATUSES
                        else None
                    )
                    await retry_pause(
                        attempt,
                        self.MAX_RETRIES,
                        subject=f'Ошибка запроса для {safe_url}',
                        error=e,
                        retry_after=retry_after,
                        base=self.RETRY_BACKOFF,
                        cap=self.MAX_BACKOFF,
                    )
                else:
                    await self.logger.log(
                        method,
                        endpoint,
                        response,
                        params,
                        response_time=time.time() - attempt_started,
                        url=url,
                    )
                    if not response.is_success:
                        response.raise_for_status()
                    return response.json()

        raise ExternalAPIError(f'Исчерпаны попытки запроса к {safe_url}')

    async def close(self) -> None:
        if self.client and not self.client.is_closed:
            await self.client.aclose()
        await self.logger.save()
