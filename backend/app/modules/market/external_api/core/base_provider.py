import logging
from typing import TYPE_CHECKING

from ..exceptions import ExternalAPIError

if TYPE_CHECKING:
    from .http_client import HTTPClient

logger = logging.getLogger(__name__)


class BaseProvider:
    NAME = ''
    DESCRIPTION = ''
    BASE_URL = ''
    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_HOUR = 100
    REQUESTS_PER_DAY = 1000
    REQUESTS_PER_MONTH = 10000
    TIMEOUT = 30
    API_KEY_REQUIRED = False

    def __init__(self, http: 'HTTPClient', api_key: str | None = None) -> None:
        self.http = http
        self._api_key = api_key

    @classmethod
    def validate_config(cls, api_key: str | None) -> list[str]:
        return []

    @property
    def name(self) -> str:
        return self.NAME or self.__class__.__name__

    async def execute(self, method_name: str, *args, **kwargs) -> dict:
        if not hasattr(self, method_name):
            raise ExternalAPIError(f'Метод {method_name} не найден в {self.name}')
        logger.info('Выполнение метода %s для %s', method_name, self.name)
        try:
            return await getattr(self, method_name)(*args, **kwargs)
        except Exception:
            logger.exception('Ошибка выполнения метода %s для %s', method_name, self.name)
            raise
        finally:
            await self.http.close()
