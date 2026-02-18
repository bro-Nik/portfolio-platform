from pydantic import BaseModel


class TokensResponse(BaseModel):
    """Ответ с парой токенов (access + refresh)."""

    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshTokenCreate(BaseModel):
    """Создание refresh токена в БД."""

    user_id: int
    token: str
    expires_at: int


class RefreshTokenUpdate(BaseModel):
    """Обновление refresh токена в БД."""

    token: str
    expires_at: int


class RefreshTokenRequest(BaseModel):
    """Запрос с refresh токеном."""

    token: str
