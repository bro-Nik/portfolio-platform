from unittest.mock import patch

import httpx
import pytest

from app.modules.market.external_api.core.http_client import HTTPClient


def make_http(async_mock, mock, *, response=None, side_effect=None):
    limiter = mock()
    ctx = mock()
    ctx.__aenter__ = async_mock()
    ctx.__aexit__ = async_mock(return_value=False)
    limiter.limit = mock(return_value=ctx)

    logger = async_mock()
    client = async_mock()
    if response is not None:
        client.request.return_value = response
    if side_effect is not None:
        client.request.side_effect = side_effect

    http = HTTPClient('https://api.test/', limiter=limiter, logger=logger)
    http._get_client = async_mock(return_value=client)
    return http, client, logger


def make_request():
    return httpx.Request('GET', 'https://api.test/v1/rates')


def status_error(status_code: int, headers: dict[str, str] | None = None) -> httpx.HTTPStatusError:
    request = make_request()
    response = httpx.Response(status_code, request=request, headers=headers or {})
    return httpx.HTTPStatusError(f'status {status_code}', request=request, response=response)


class TestHttpClientRetryPolicy:
    async def test_4xx_not_retried(self, async_mock, mock):
        http, client, _ = make_http(async_mock, mock, side_effect=status_error(400))

        with pytest.raises(httpx.HTTPStatusError):
            await http.request('GET', 'v1/rates')

        assert client.request.await_count == 1

    async def test_401_not_retried(self, async_mock, mock):
        http, client, _ = make_http(async_mock, mock, side_effect=status_error(401))

        with pytest.raises(httpx.HTTPStatusError):
            await http.request('GET', 'v1/rates')

        assert client.request.await_count == 1

    async def test_5xx_retried_until_success(self, async_mock, mock):
        ok = httpx.Response(200, json={'ok': True}, request=make_request())
        http, client, _ = make_http(async_mock, mock, side_effect=[status_error(500), ok])

        with patch('asyncio.sleep', new=async_mock()):
            result = await http.request('GET', 'v1/rates')

        assert result == {'ok': True}
        assert client.request.await_count == 2

    async def test_429_retried_after_retry_after(self, async_mock, mock):
        ok = httpx.Response(200, json={'ok': True}, request=make_request())
        http, client, _ = make_http(
            async_mock,
            mock,
            side_effect=[status_error(429, {'Retry-After': '1'}), ok],
        )

        with patch('asyncio.sleep', new=async_mock()) as sleep:
            result = await http.request('GET', 'v1/rates')

        assert result == {'ok': True}
        assert client.request.await_count == 2
        sleep.assert_awaited_once_with(1.0)


class TestHttpClientRequestLogging:
    async def test_one_log_per_attempt(self, async_mock, mock):
        # Раньше успешный ответ логировался до проверки is_success, а неуспешный
        # логировался ещё раз в except: ретраи удваивали строки в request_log и
        # завышали счётчики провайдера в админке.
        ok = httpx.Response(200, json={'ok': True}, request=make_request())
        http, _, logger = make_http(async_mock, mock, side_effect=[status_error(500), ok])

        with patch('asyncio.sleep', new=async_mock()):
            await http.request('GET', 'v1/rates')

        assert logger.log.await_count == 2

    async def test_single_attempt_logs_once(self, async_mock, mock):
        ok = httpx.Response(200, json={'ok': True}, request=make_request())
        http, _, logger = make_http(async_mock, mock, response=ok)

        await http.request('GET', 'v1/rates')

        assert logger.log.await_count == 1

    async def test_api_key_not_leaked_into_error_log(self, async_mock, mock):
        error = httpx.HTTPStatusError(
            "Client error '429 Too Many Requests' for url 'https://api.test/live?access_key=SECRET'",
            request=make_request(),
            response=httpx.Response(429, request=make_request()),
        )
        http, _, logger = make_http(async_mock, mock, side_effect=error)

        with pytest.raises(httpx.HTTPStatusError), patch('asyncio.sleep', new=async_mock()):
            await http.request('GET', 'live')

        logged_error = logger.log.await_args.kwargs['error']
        assert 'SECRET' not in logged_error
        assert 'access_key=***' in logged_error

    async def test_retry_after_honored_on_503(self, async_mock, mock):
        ok = httpx.Response(200, json={'ok': True}, request=make_request())
        http, client, _ = make_http(
            async_mock,
            mock,
            side_effect=[status_error(503, {'Retry-After': '2'}), ok],
        )

        with patch('asyncio.sleep', new=async_mock()) as sleep:
            await http.request('GET', 'v1/rates')

        assert client.request.await_count == 2
        sleep.assert_awaited_once_with(2.0)
