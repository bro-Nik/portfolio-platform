import logging
from typing import TYPE_CHECKING

from app.external_api.exceptions import ExternalAPIError

if TYPE_CHECKING:
    from app.external_api.core.http_client import HTTPClient

logger = logging.getLogger(__name__)


class BaseProvider:
    """Базовый класс для API провайдеров."""

    NAME = ''
    DESCRIPTION = ''
    BASE_URL = ''
    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_HOUR = 100
    REQUESTS_PER_DAY = 1000
    REQUESTS_PER_MONTH = 10000
    TIMEOUT = 30

    def __init__(self, http: 'HTTPClient') -> None:
        self.http = http

    @property
    def name(self) -> str:
        return self.NAME or self.__class__.__name__

    async def execute(self, method_name: str, *args: list, **kwargs) -> dict:
        """Выполнить метод провайдера."""
        if not hasattr(self, method_name):
            raise ExternalAPIError('Метод {method_name} не найден у провайдера {self.provider}')

        logger.info('Выполнение метода %s для %s', method_name, self.name)
        try:
            return await getattr(self, method_name)(*args, **kwargs)
        except Exception:
            logger.exception('Ошибка выполнения метода %s для %s', method_name, self.name)
            raise
        finally:
            await self.http.close()
