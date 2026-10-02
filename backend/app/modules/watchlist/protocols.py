from typing import Protocol


class UserEmailReader(Protocol):
    """Порт чтения контактных email пользователей.

    Реализуется модулем auth: watchlist не знает о его таблицах.
    Возвращает адреса только подтверждённых (verified) пользователей —
    на неподтверждённый адрес уведомления не отправляются.
    """

    async def get_emails(self, user_ids: list[int]) -> dict[int, str]:
        """Email подтверждённых пользователей из списка."""
        ...
