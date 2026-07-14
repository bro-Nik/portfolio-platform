from pydantic import BaseModel


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshTokenCreate(BaseModel):
    user_id: int
    token: str
    expires_at: int


class RefreshTokenUpdate(BaseModel):
    token: str
    expires_at: int


class RefreshTokenRequest(BaseModel):
    token: str
