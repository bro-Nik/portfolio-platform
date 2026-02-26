class BusinessError(Exception):
    """Базовое бизнес-исключение."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AuthenticationError(BusinessError):
    """Ошибка аутентификации."""

    def __init__(self, message: str = 'Ошибка аутентификации') -> None:
        super().__init__(message)


class PermissionDeniedError(BusinessError):
    """Недостаточно прав."""

    def __init__(self, message: str = 'Недостаточно прав') -> None:
        super().__init__(message)


class NotFoundError(BusinessError):
    """Ресурс не найден."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConflictError(BusinessError):
    """Конфликт (уже существует)."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class BusinessRuleError(BusinessError):
    """Нарушение бизнес-правила."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
