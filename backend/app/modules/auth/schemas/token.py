from pydantic import BaseModel


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class RefreshTokenCreate(BaseModel):
    user_id: int
    token_hash: str
    expires_at: int


class RefreshTokenUpdate(BaseModel):
    token_hash: str
    expires_at: int


class RefreshTokenRequest(BaseModel):
    token: str


class VerifyEmailRequest(BaseModel):
    token: str
