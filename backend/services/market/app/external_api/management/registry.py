from typing import Dict, Optional, Type

from app.external_api.providers.base import ApiProviderBase


class ApiProviderRegistry:
    """Реестр внешних API провайдеров"""

    PROVIDERS: Dict[str, Type[ApiProviderBase]] = {}

    @classmethod
    def register_provider(cls):
        """Декоратор для регистрации провайдеров"""
        def decorator(provider_class: Type[ApiProviderBase]):
            cls.PROVIDERS[provider_class.NAME] = provider_class
            return provider_class
        return decorator

    @classmethod
    def get_provider(cls, provider_name: str) -> Optional[ApiProviderBase]:
        """Получает по имени провайдера"""
        provider_class = cls.PROVIDERS.get(provider_name)
        if provider_class:
            return provider_class()

    @classmethod
    def get_provider_methods(cls, provider_name: str) -> dict:
        """Получает методы по имени провайдера"""
        methods = {}
        provider = cls.get_provider(provider_name)
        if provider:
            for name, func in vars(provider.methods).items():
                if not name.startswith('_'):
                    methods[name] = func
        return methods


registry = ApiProviderRegistry()
