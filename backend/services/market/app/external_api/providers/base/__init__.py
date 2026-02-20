from abc import ABC


class ApiProviderBase(ABC):
    """Базовый класс для API провайдеров"""
    NAME = ''
    DISPLAY_NAME = ''
    DESCRIPTION = ''
    REQUESTS_PER_MINUTE = 30
    REQUESTS_PER_HOUR = 100
    REQUESTS_PER_DAY = 1000
    REQUESTS_PER_MONTH = 10000
    TIMEOUT = 30
    API_KEY_NOTE = 'Ключ не обязателен для бесплатного тарифа'

    def __init__(self):
        self.client = None
        self.methods = None

    @property
    def name(self) -> str:
        if not self.NAME:
            raise ValueError(f'Не задано "NAME" для {self.__class__.__name__}')
        return self.NAME

    def has_method(self, method_name):
        return hasattr(self.methods, method_name)

    def execute(self, method_name, *args, **kwargs):
        if not self.has_method(method_name):
            raise ValueError(f'API провайдер "{self.name}" не имеет метода {method_name}')

        method = getattr(self.methods, method_name)
        result = method(*args, **kwargs)
        return result

    def save_state(self):
        """Сохранение состояния"""
        if self.client and hasattr(self.client, 'save_state'):
            self.client.save_state()
