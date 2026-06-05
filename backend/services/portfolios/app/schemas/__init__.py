from shared.schemas import AuthUser, Context, UserRole

from .tag import TagAttachRequest, TagCreate, TagResponse, TagUpdate
from .portfolio import (
    PortfolioCreate,
    PortfolioCreateRequest,
    PortfolioDeleteResponse,
    PortfolioListResponse,
    PortfolioResponse,
    PortfolioUpdate,
    PortfolioUpdateRequest,
)
from .portfolio_asset import (
    PortfolioAssetCreate,
    PortfolioAssetCreateRequest,
    PortfolioAssetResponse,
    PortfolioAssetUpdate,
)
from .transaction import (
    TransactionCreate,
    TransactionCreateRequest,
    TransactionResponse,
    TransactionResponseWithAssets,
    TransactionUpdate,
    TransactionUpdateRequest,
)
from .wallet import (
    WalletCreate,
    WalletCreateRequest,
    WalletDeleteResponse,
    WalletListResponse,
    WalletResponse,
    WalletUpdate,
    WalletUpdateRequest,
)
from .wallet_asset import (
    WalletAssetCreate,
    WalletAssetResponse,
    WalletAssetUpdate,
)

# Перестраиваем модели с форвард-декларациями
PortfolioResponse.model_rebuild()
PortfolioListResponse.model_rebuild()
WalletResponse.model_rebuild()
TransactionResponseWithAssets.model_rebuild()
