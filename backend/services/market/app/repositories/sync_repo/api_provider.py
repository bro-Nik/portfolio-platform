from shared.repositories import BaseSyncRepository as BaseRepository
from sqlalchemy.orm import Session

from app import models, schemas


class ApiProviderRepository(
    BaseRepository[models.ApiProvider, schemas.ApiProviderCreate, schemas.ApiProviderUpdate]
):
    def __init__(self, session: Session):
        super().__init__(models.ApiProvider, session)

    # Алисы для обратной совместимости (временно)
    def get_by_name(self, name: str) -> models.ApiProvider | None:
        return self.get_by(self.model.name == name)

    def get_with_forupdate(self, id: int) -> models.ApiProvider | None:
        return self.get(id, for_update=True)

    def get_by_name_with_forupdate(self, name: str) -> models.ApiProvider | None:
        return self.get_by(self.model.name == name, for_update=True)
