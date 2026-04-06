from collections.abc import Awaitable, Callable
import functools
import logging
from typing import Any, ParamSpec, TypeVar, cast

logger = logging.getLogger(__name__)

P = ParamSpec('P')
T = TypeVar('T')


def handle_task_errors(
    default_message: str = 'Ошибка при выполнении задачи',
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[dict[str, Any]]]]:
    """Декоратор для обработки исключений в TaskIQ задачах.

    Пример:
        @broker.task
        @handle_task_errors("Ошибка обновления цен")
        async def update_prices(provider: str, db_task_id: int, **kwargs):
            ...

    """
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[dict[str, Any]]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            task_id = kwargs.get('db_task_id', 'unknown')

            try:
                return await func(*args, **kwargs)

            except Exception as e:
                logger.exception('Ошибка в задаче %s', task_id)

                return {'status': 'error', 'error': default_message, 'details': str(e)}
        return cast('Callable[P, Awaitable[dict[str, Any]]]', wrapper)
    return decorator


class ExternalAPIError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
