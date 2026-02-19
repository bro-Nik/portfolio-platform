from sqlalchemy.orm import Session

from app import models, schemas
from .base import BaseRepository


class ApiProviderRepository(
    BaseRepository[models.ApiProvider, schemas.ApiProviderCreate, schemas.ApiProviderUpdate]
):
    def __init__(self, db: Session):
        super().__init__(models.ApiProvider, db)
