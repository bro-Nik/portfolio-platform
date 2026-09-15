import pytest

from app.modules.market.external_api.core.request_logger import (
    RequestLogger,
    _sanitize_params,
    _sanitize_url,
    sanitize_error,
)


class TestSanitizeParams:
    def test_redacts_secret_keys(self):
        params = {'access_key': 'secret1', 'api_key': 'secret2', 'apiKey': 'secret3', 'page': 1, 'market': 'stocks'}

        result = _sanitize_params(params)

        assert result == {'access_key': '***', 'api_key': '***', 'apiKey': '***', 'page': 1, 'market': 'stocks'}

    def test_empty_params(self):
        assert _sanitize_params({}) == {}
        assert _sanitize_params(None) == {}


class TestSanitizeUrl:
    def test_redacts_secret_query_params(self):
        url = 'https://api.test/v3/reference/tickers?apiKey=SECRET&market=stocks&access_key=other'

        result = _sanitize_url(url)

        assert result == 'https://api.test/v3/reference/tickers?apiKey=***&market=stocks&access_key=***'

    def test_url_without_query_unchanged(self):
        url = 'https://api.test/v1/rates'

        assert _sanitize_url(url) == url

    def test_empty_url(self):
        assert _sanitize_url(None) == ''
        assert _sanitize_url('') == ''


class TestRequestLoggerLog:
    async def test_log_redacts_params_and_url(self, async_mock):
        logger = RequestLogger('CurrencyLayer', 1, session_factory=async_mock())

        await logger.log(
            'GET',
            'live',
            None,
            {'access_key': 'secret'},
            response_time=0.1,
            url='https://api.test/v1/rates?access_key=secret',
        )

        log = logger._logs[0]
        assert log.request_params == {'access_key': '***'}
        assert log.request_url == 'https://api.test/v1/rates?access_key=***'
        assert log.error_message is None


class TestSanitizeError:
    def test_redacts_key_from_httpx_error_message(self):
        # str(HTTPStatusError) embeds the full request URL, query string included.
        error = (
            "Client error '429 Too Many Requests' for url "
            "'https://api.test/v3/aggs/ticker/x?apiKey=SECRET&market=stocks'\n"
            'For more information check: https://developer.mozilla.org/...'
        )

        result = sanitize_error(error)

        assert 'SECRET' not in result
        assert 'apiKey=***' in result
        assert 'market=stocks' in result

    @pytest.mark.parametrize('pattern', ['access_key=', 'apikey=', 'token=', 'secret=', 'password='])
    def test_redacts_common_secret_params(self, pattern):
        result = sanitize_error(f"url 'https://api.test/x?{pattern}LEAK&page=1'")

        assert 'LEAK' not in result
        assert f'{pattern}***' in result

    def test_truncates_long_error(self):
        assert len(sanitize_error('x' * 5000)) == 500

    def test_none_and_empty(self):
        assert sanitize_error(None) is None
        assert sanitize_error('') == ''


class TestRequestLoggerErrorMessage:
    async def test_error_message_is_sanitized(self, async_mock):
        logger = RequestLogger('CurrencyLayer', 1, session_factory=async_mock())

        await logger.log(
            'GET',
            'live',
            None,
            {'access_key': 'secret'},
            response_time=0.1,
            error="Client error '401' for url 'https://api.test/live?access_key=SECRET'",
        )

        log = logger._logs[0]
        assert 'SECRET' not in log.error_message
        assert 'access_key=***' in log.error_message

    async def test_error_body_is_sanitized(self, async_mock):
        import httpx

        logger = RequestLogger('Polygon', 1, session_factory=async_mock())
        response = httpx.Response(
            403,
            json={'error': 'invalid apiKey=SECRET'},
            request=httpx.Request('GET', 'https://api.polygon.io/x'),
        )

        await logger.log(
            'GET',
            'v3/reference/tickers/AAPL',
            response,
            {},
            response_time=0.2,
            url='https://api.polygon.io/v3/reference/tickers/AAPL?apiKey=SECRET',
        )

        log = logger._logs[0]
        assert 'SECRET' not in log.error_message
