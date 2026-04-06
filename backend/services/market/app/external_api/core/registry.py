from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from app.external_api.core.base_provider import BaseProvider
from app.external_api.exceptions import ExternalAPIError
from app.external_api.methods.base import MethodBase

P = ParamSpec('P')
F = TypeVar('F', bound=Callable[..., Any])


class ProviderRegistry:
    """Реестр внешних API провайдеров."""

    PROVIDERS: dict[str, type[BaseProvider]] = {}

    @classmethod
    def register_provider(cls) -> Callable:
        """Декоратор для регистрации провайдеров."""
        def decorator(provider_class: type[BaseProvider]) -> Callable:
            cls.PROVIDERS[provider_class.NAME] = provider_class
            return provider_class
        return decorator

    @classmethod
    def register_method(cls, method: MethodBase, **kwargs) -> Callable:
        """Декоратор для пометки методов провайдера."""
        def decorator(func: Callable) -> Callable:
            func.__dict__['api_method_info'] = {
                'name': method.name,
                'description': method.description,
                'exemple_params': method.exemple_params,
                **kwargs,
            }
            return func
        return decorator

    @classmethod
    def get_provider(cls, name: str) -> type[BaseProvider]:
        """Получает по имени провайдера."""
        provider_class = cls.PROVIDERS.get(name)
        if not provider_class:
            raise ExternalAPIError(f'API провайдер {name} не найден')

        return provider_class

    @classmethod
    def get_provider_methods(cls, name: str) -> list[dict]:
        """Получает методы по имени провайдера."""
        provider = cls.get_provider(name)

        methods = []
        for attr_name in dir(provider):
            attr = getattr(provider, attr_name)
            method_info = getattr(attr, 'api_method_info', None)
            if method_info:
                methods.append({'name': attr_name, 'method': attr_name, **method_info})
        return methods


registry = ProviderRegistry()
