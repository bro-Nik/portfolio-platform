from app.modules.market.external_api.core.request_logger import (
    RequestLogger,
    _sanitize_params,
    _sanitize_url,
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
            'GET', 'live', None, {'access_key': 'secret'}, response_time=0.1,
            url='https://api.test/v1/rates?access_key=secret',
        )

        log = logger._logs[0]
        assert log.request_params == {'access_key': '***'}
        assert log.request_url == 'https://api.test/v1/rates?access_key=***'
        assert log.error_message is None
