from pydantic import BaseModel

from app.common.schemas import ApiModel


class TokensResponse(ApiModel):
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


class RefreshTokenRequest(ApiModel):
    token: str


class VerifyEmailRequest(ApiModel):
    token: str
