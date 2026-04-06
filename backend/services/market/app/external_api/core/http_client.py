import logging
import time
from typing import Any

import httpx

from app.external_api.core.rate_limiter import RateLimiter
from app.external_api.core.request_logger import RequestLogger

logger = logging.getLogger(__name__)


class HTTPClient:
    """HTTP клиент с rate limiting и логированием."""

    TIMEOUT = 30.0  # секунд
    MAX_CONNECTIONS = 100  # максимальное количество соединений
    MAX_KEEPALIVE_CONNECTIONS = 20  # keep-alive соединений

    def __init__(self, base_url: str, limiter: RateLimiter, logger: RequestLogger) -> None:
        self.base_url = base_url
        self.limiter = limiter
        self.logger = logger
        self.client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self.client is None or self.client.is_closed:
            # Настройка клиента с пулом соединений
            limits = httpx.Limits(
                max_connections=self.MAX_CONNECTIONS,
                max_keepalive_connections=self.MAX_KEEPALIVE_CONNECTIONS,
                keepalive_expiry=30.0,
            )

            self.client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.TIMEOUT),
                limits=limits,
                headers={
                    'User-Agent': 'Crypto-Tracker/1.0',
                    'Accept': 'application/json',
                },
            )
        return self.client

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
        """Выполнить асинхронный запрос с учетом rate limiting.

        Args:
            method: HTTP метод
            endpoint: endpoint API
            params: query параметры
            data: form data
            json_data: JSON данные
            headers: заголовки

        Returns:
            Dict с ответом API

        Raises:
            httpx.HTTPError: при ошибке запроса

        """
        start_time = time.time()
        client = await self._get_client()
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        # Объединяем заголовки
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            # Ожидаем разрешения от rate limiter
            async with self.limiter.limit():
                logger.debug('Выполнить запрос к %s', url)

                # Выполняем асинхронный запрос
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    headers=request_headers,
                    timeout=timeout or self.TIMEOUT,
                )

                await self.logger.log(
                    method, endpoint, response, params,
                    response_time=time.time() - start_time,
                )

                # Проверяем на ошибки
                if not response.is_success:
                    logger.error(f'API request failed: {response.status_code} - {response.text[:200]}')
                    response.raise_for_status()

                # Возвращаем JSON
                return response.json()

        except Exception as e:
            await self.logger.log(
                method, endpoint, response, params,
                response_time=time.time() - start_time,
                error=str(e),
            )

            logger.error(f'Unexpected error for {url}: {e}')
            raise

    async def close(self) -> None:
        """Закрыть HTTP клиент и сохранить логи."""
        if self.client and not self.client.is_closed:
            await self.client.aclose()

        await self.logger.save()
