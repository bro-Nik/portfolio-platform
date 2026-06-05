from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .tag import TagResponse


class WalletAssetBase(BaseModel):
    """Базовые поля."""

    wallet_id: int
    ticker_id: str


class WalletAssetCreate(WalletAssetBase):
    """Создание актива в БД."""

    user_id: int


class WalletAssetUpdate(WalletAssetBase):
    """Обновление актива в БД."""


class WalletAssetResponse(WalletAssetBase):
    """Ответ с данными актива."""

    id: int
    quantity: Decimal
    buy_orders: Decimal
    tags: list[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)
