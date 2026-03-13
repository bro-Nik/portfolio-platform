from sqlalchemy.orm import Session

from app.models import Provider
from app.repositories import BaseSyncRepository
from app.schemas import ProviderCreate, ProviderUpdate


class SyncProviderRepository(BaseSyncRepository[Provider, ProviderCreate, ProviderUpdate]):
    """Репозиторий для работы с API провайдерами."""

    def __init__(self, session: Session) -> None:
        super().__init__(Provider, session)

    def get_by_name(self, name: str, *, for_update: bool = False) -> Provider | None:
        """Получить API провайдера по названию."""
        return self.get_by(Provider.name == name, for_update=for_update)
