from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from .base_provider import BaseProvider
from ..exceptions import ExternalAPIError
from ..methods.base import MethodBase

P = ParamSpec('P')
F = TypeVar('F', bound=Callable[..., Any])


class ProviderRegistry:
    PROVIDERS: dict[str, type[BaseProvider]] = {}

    @classmethod
    def register_provider(cls) -> Callable:
        def decorator(provider_class: type[BaseProvider]) -> Callable:
            cls.PROVIDERS[provider_class.NAME] = provider_class
            return provider_class
        return decorator

    @classmethod
    def register_method(cls, method: MethodBase, **kwargs) -> Callable:
        def decorator(func: Callable) -> Callable:
            func.__dict__['api_method_info'] = {
                'name': method.name,
                'description': method.description,
                'example_params': method.exemple_params,
                'parameters_schema': method.parameters_schema,
                **kwargs,
            }
            return func
        return decorator

    @classmethod
    def get_provider(cls, name: str) -> type[BaseProvider]:
        provider_class = cls.PROVIDERS.get(name)
        if not provider_class:
            raise ExternalAPIError(f'API провайдер {name} не найден')
        return provider_class

    @classmethod
    def get_provider_methods(cls, name: str) -> list[dict]:
        provider = cls.get_provider(name)
        methods = []
        for attr_name in dir(provider):
            attr = getattr(provider, attr_name)
            method_info = getattr(attr, 'api_method_info', None)
            if method_info:
                methods.append({'name': attr_name, 'method': attr_name, **method_info})
        return methods


registry = ProviderRegistry()
