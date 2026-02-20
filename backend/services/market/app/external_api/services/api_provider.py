from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ApiProvider
from app.repositories.sync_repo.api_provider import ApiProviderRepository


class ApiProviderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ApiProviderRepository(db)

    def get_provider(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None
    ) -> Optional[ApiProvider]:
        if id:
            return self.repo.get(id)
        if name:
            return self.repo.get_by_name(name)

    def get_provider_whith_lock(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None
    ) -> Optional[ApiProvider]:
        if id:
            return self.repo.get_with_forupdate(id)
        if name:
            return self.repo.get_by_name_with_forupdate(name)
