from app.external_api.management.registry import registry
from app.external_api.providers.base import ApiProviderBase
from .client import CoingeckoClient
from .methods import CoingeckoMethods


@registry.register_provider()
class CoingeckoProvider(ApiProviderBase):
    NAME = 'coingecko'
    DISPLAY_NAME = 'Coingecko'
    DESCRIPTION = 'Криптовалютные данные и цены'
    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_HOUR = 100
    REQUESTS_PER_DAY = 10000
    REQUESTS_PER_MONTH = 100000
    TIMEOUT = 30
    API_KEY_NOTE = 'Ключ не обязателен для бесплатного тарифа'

    def __init__(self):
        self.client = CoingeckoClient(self.name)
        self.methods = CoingeckoMethods(self.client)
