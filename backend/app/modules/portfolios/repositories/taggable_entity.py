from sqlalchemy.ext.asyncio import AsyncSession

from .portfolio import PortfolioRepository
from .portfolio_asset import PortfolioAssetRepository
from .wallet import WalletRepository
from .wallet_asset import WalletAssetRepository
from app.modules.tags.protocols import EntityOwnershipChecker


class TaggableEntityOwnershipRepository(EntityOwnershipChecker):
    """Проверка владения сущностями, к которым прикрепляются теги.

    Живёт в portfolios (владеет этими таблицами), для tags доступен через порт.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repos = {
            'portfolio': PortfolioRepository(session),
            'wallet': WalletRepository(session),
            'portfolio_asset': PortfolioAssetRepository(session),
            'wallet_asset': WalletAssetRepository(session),
        }

    async def owns_entity(self, entity_type: str, entity_id: int, user_id: int) -> bool:
        repo = self._repos.get(entity_type)
        if repo is None:
            return False
        entity = await repo.get(entity_id)
        return entity is not None and entity.user_id == user_id
