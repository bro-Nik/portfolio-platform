from pydantic import BaseModel

from app.common.schemas import ApiModel

from app.common.utils.decimal import CleanDecimal
from app.modules.tags.schemas import TagResponse


class WalletBase(ApiModel):
    name: str
    comment: str | None = None


class WalletCreateRequest(WalletBase):
    pass


class WalletUpdateRequest(WalletBase):
    pass


class WalletArchiveRequest(ApiModel):
    is_archived: bool


class WalletAssetArchiveRequest(ApiModel):
    is_archived: bool


class WalletCreate(WalletBase):
    user_id: int


class WalletUpdate(WalletBase):
    pass


class WalletAssetBase(ApiModel):
    wallet_id: int
    ticker_id: int


class WalletAssetCreate(WalletAssetBase):
    user_id: int


class WalletAssetUpdate(WalletAssetBase):
    pass


class WalletAssetResponse(WalletAssetBase):
    id: int
    quantity: CleanDecimal
    buy_orders: CleanDecimal
    sell_orders: CleanDecimal
    is_archived: bool
    has_transactions: bool = False
    tags: list[TagResponse] = []
    name: str | None = None
    symbol: str | None = None
    image: str | None = None
    market: str | None = None


class WalletResponse(WalletBase):
    id: int
    is_archived: bool
    has_transactions: bool = False
    assets: list[WalletAssetResponse] = []
    tags: list[TagResponse] = []


class WalletListResponse(ApiModel):
    wallets: list[WalletResponse]


WalletResponse.model_rebuild()
