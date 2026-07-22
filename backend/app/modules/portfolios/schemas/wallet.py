from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .tag import TagResponse


class WalletBase(BaseModel):
    name: str
    comment: str | None = None


class WalletCreateRequest(WalletBase):
    pass


class WalletUpdateRequest(WalletBase):
    pass


class WalletCreate(WalletBase):
    user_id: int


class WalletUpdate(WalletBase):
    pass


class WalletAssetBase(BaseModel):
    wallet_id: int
    ticker_id: int


class WalletAssetCreate(WalletAssetBase):
    user_id: int


class WalletAssetUpdate(WalletAssetBase):
    pass


class WalletAssetResponse(WalletAssetBase):
    id: int
    quantity: Decimal
    buy_orders: Decimal
    is_archived: bool
    has_transactions: bool = False
    tags: list[TagResponse] = []
    name: str | None = None
    symbol: str | None = None
    image: str | None = None
    model_config = ConfigDict(from_attributes=True)


class WalletResponse(WalletBase):
    id: int
    is_archived: bool
    has_transactions: bool = False
    assets: list[WalletAssetResponse] = []
    tags: list[TagResponse] = []
    model_config = ConfigDict(from_attributes=True)


class WalletListResponse(BaseModel):
    wallets: list[WalletResponse]


class WalletDeleteResponse(BaseModel):
    wallet_id: int


WalletResponse.model_rebuild()
