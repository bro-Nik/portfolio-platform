class BusinessError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class AuthenticationError(BusinessError):
    def __init__(self, message: str = 'Ошибка аутентификации') -> None:
        super().__init__(message)


class PermissionDeniedError(BusinessError):
    def __init__(self, message: str = 'Недостаточно прав') -> None:
        super().__init__(message)


class NotFoundError(BusinessError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ConflictError(BusinessError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class BusinessRuleError(BusinessError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
