from collections.abc import Callable
import functools
from typing import Any, ParamSpec, TypeVar, cast

from fastapi import HTTPException, status

from .business import (
    AuthenticationError,
    BusinessRuleError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)

P = ParamSpec('P')
F = TypeVar('F', bound=Callable[..., Any])


def handle_errors(
    default_message: str = 'Ошибка при выполнении операции',
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except AuthenticationError as e:
                raise UnauthorizedException(str(e)) from e
            except PermissionDeniedError as e:
                raise ForbiddenException(str(e)) from e
            except NotFoundError as e:
                raise NotFoundException(str(e)) from e
            except ConflictError as e:
                raise ConflictException(str(e)) from e
            except BusinessRuleError as e:
                raise BadRequestException(str(e)) from e
            except Exception as e:
                raise InternalServerException(f'{default_message}: {e!s}') from e
        return cast('F', wrapper)
    return decorator


class BadRequestException(HTTPException):
    def __init__(self, detail: str = 'Неверный запрос') -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = 'Необходима авторизация') -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={'WWW-Authenticate': 'Bearer'},
        )


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = 'Недостаточно прав') -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class NotFoundException(HTTPException):
    def __init__(self, detail: str = 'Ресурс не найден') -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ConflictException(HTTPException):
    def __init__(self, detail: str = 'Конфликт данных') -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InternalServerException(HTTPException):
    def __init__(self, detail: str = 'Внутренняя ошибка сервера') -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )
