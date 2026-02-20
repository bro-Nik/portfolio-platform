from typing import Any
import logging

from app.external_api.services.task_tracker import ApiTaskTracker
from app.external_api.management.registry import registry


logger = logging.getLogger(__name__)


class ApiManager:
    """Менеджер для работы с внешними API"""

    def __init__(self, provider_name: str):
        self.api_provider = registry.get_provider(provider_name)
        if not self.api_provider:
            raise ValueError(f'API провайден "{provider_name}" не найден')

        self.task_tracker = ApiTaskTracker()


    def execute(self, method_name: str, *args, **kwargs) -> Any:
        """Выполнить метод API"""
        if not self.api_provider:
            return

        logger.info('Выполнение метода %s для %s', method_name, self.api_provider.name)

        # Сообщаем трекеру задач о начале
        self.task_tracker.started(kwargs.get('db_task_id', ''))

        try:
            # Выполняем метод
            result = self.api_provider.execute(method_name, *args, **kwargs)

            # Сообщаем трекеру задач о завершении
            self.task_tracker.completed(kwargs.get('db_task_id', ''))

            return result

        except Exception as e:
            logger.error('Ошибка при выполнении метода %s: %s', method_name, e)

            # Сообщаем трекеру задач о падении
            self.task_tracker.error(kwargs.get('db_task_id', ''), e)

            raise

        finally:
            # Принудительно сохраняем все состояние
            self.save_state()

    def save_state(self):
        """Сохранение состояния"""
        if self.api_provider and hasattr(self.api_provider, 'save_state'):
            try:
                self.api_provider.save_state()
            except Exception as e:
                logger.error('Ошибка при сохранении состояния: %s', e)
