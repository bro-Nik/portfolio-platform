
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictError, NotFoundError, PermissionDeniedError

from app.modules.portfolios.models import Portfolio, PortfolioAsset, Transaction
from app.modules.portfolios.protocols import TagReader
from app.modules.portfolios.repositories import (
    PortfolioRepository, TransactionRepository,
)
from app.modules.portfolios.schemas import (
    PortfolioAssetCreateRequest,
    PortfolioCreate, PortfolioCreateRequest, PortfolioUpdate, PortfolioUpdateRequest,
)
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.common.schemas import Context


class PortfolioService:
    ENTITY_TYPE = 'portfolio'
    ASSET_ENTITY_TYPE = 'portfolio_asset'

    def __init__(self, session: AsyncSession, ctx: Context, *, taggable_repo: TagReader) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = PortfolioRepository(session)
        self.asset_service = PortfolioAssetService(ctx, session)
        self.taggable_repo = taggable_repo
        self.transaction_repo = TransactionRepository(session)

    async def _bulk_load_tags(self, portfolios: list[Portfolio]) -> None:
        items = []
        for p in portfolios:
            items.append((self.ENTITY_TYPE, p.id))
            for a in p.assets:
                items.append((self.ASSET_ENTITY_TYPE, a.id))
        tags_map = await self.taggable_repo.bulk_get_tags(items)
        for portfolio in portfolios:
            portfolio.tags = tags_map.get((self.ENTITY_TYPE, portfolio.id), [])
            for asset in portfolio.assets:
                asset.tags = tags_map.get((self.ASSET_ENTITY_TYPE, asset.id), [])

    async def get(self, id: int) -> Portfolio:
        portfolio = await self.repo.get(id)
        self._verify(portfolio)
        return portfolio

    async def get_with_assets(self, id: int) -> Portfolio:
        portfolio = await self.repo.get_with_assets(id)
        self._verify(portfolio)
        await self._bulk_load_tags([portfolio])
        return portfolio

    async def get_all_with_assets(self) -> list[Portfolio]:
        portfolios = await self.repo.get_all_by_user_with_assets(self.actor.id)
        await self._bulk_load_tags(portfolios)
        return portfolios

    async def create(self, data: PortfolioCreateRequest) -> Portfolio:
        await self._validate_unique_name(data.name)
        portfolio = await self.repo.create(PortfolioCreate(**data.model_dump(), user_id=self.actor.id).model_dump())
        await self.session.commit()
        return portfolio

    async def update(self, id: int, data: PortfolioUpdateRequest) -> Portfolio:
        portfolio = await self.get(id)
        if portfolio.is_archived:
            raise ConflictError('Нельзя редактировать архивный портфель')
        if data.name != portfolio.name:
            await self._validate_unique_name(data.name)
        updated = await self.repo.update(id, PortfolioUpdate(**data.model_dump()).model_dump())
        await self.session.commit()
        return updated

    async def delete(self, id: int) -> None:
        portfolio = await self.get(id)
        has_txns = await self.transaction_repo.exists_for_portfolio(id)
        if has_txns:
            raise ConflictError('Нельзя удалить портфель с транзакциями')
        await self.repo.delete(id)
        await self.session.commit()

    async def archive(self, id: int) -> None:
        portfolio = await self.repo.get_with_assets(id)
        self._verify(portfolio)
        await self.repo.update(id, {'is_archived': True})
        unarchived_ids = [a.id for a in portfolio.assets if not a.is_archived]
        if unarchived_ids:
            await self.asset_service.archive_many(unarchived_ids)
        await self.session.commit()

    async def unarchive(self, id: int) -> None:
        await self.get(id)
        await self.repo.update(id, {'is_archived': False})
        await self.session.commit()

    async def add_asset(self, id: int, data: PortfolioAssetCreateRequest) -> PortfolioAsset:
        portfolio = await self.get(id)
        if portfolio.is_archived:
            raise ConflictError('Нельзя добавлять активы в архивный портфель')
        asset = await self.asset_service.create(data)
        await self.session.commit()
        return asset

    async def delete_asset(self, id: int, asset_id: int) -> None:
        await self.get(id)
        await self.asset_service.delete(asset_id)
        await self.session.commit()

    async def archive_asset(self, id: int, asset_id: int) -> None:
        await self.get(id)
        await self.asset_service.archive(asset_id)
        await self.session.commit()

    async def unarchive_asset(self, id: int, asset_id: int) -> None:
        await self.get(id)
        await self.asset_service.unarchive(asset_id)
        await self.session.commit()

    async def handle_transaction(self, t: Transaction, *, cancel: bool = False) -> None:
        if not t.portfolio_id:
            return
        await self.asset_service.handle_transaction(t, cancel=cancel)

    async def _validate_unique_name(self, name: str) -> None:
        if await self.repo.exists_by_name_and_user(name, self.actor.id):
            raise ConflictError('Портфель с таким именем уже существует')

    def _verify(self, obj) -> None:
        if not obj:
            raise NotFoundError('Портфель не найден')
        if obj.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав')
