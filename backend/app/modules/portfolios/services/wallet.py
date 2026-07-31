from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import ConflictError, NotFoundError, PermissionDeniedError

from app.modules.portfolios.models import Wallet, Transaction
from app.modules.portfolios.repositories import (
    TransactionRepository, WalletRepository,
)
from app.modules.tags.repositories import TaggableRepository
from app.modules.portfolios.schemas import (
    WalletCreate, WalletCreateRequest, WalletUpdate, WalletUpdateRequest,
)
from app.modules.portfolios.services.wallet_asset import WalletAssetService
from app.common.schemas import Context


class WalletService:
    ENTITY_TYPE = 'wallet'
    ASSET_ENTITY_TYPE = 'wallet_asset'

    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = WalletRepository(session)
        self.asset_service = WalletAssetService(ctx, session)
        self.taggable_repo = TaggableRepository(session)
        self.transaction_repo = TransactionRepository(session)

    async def _bulk_load_tags(self, wallets: list[Wallet]) -> None:
        items = []
        for w in wallets:
            items.append((self.ENTITY_TYPE, w.id))
            for a in w.assets:
                items.append((self.ASSET_ENTITY_TYPE, a.id))
        tags_map = await self.taggable_repo.bulk_get_tags(items)
        for wallet in wallets:
            wallet.tags = tags_map.get((self.ENTITY_TYPE, wallet.id), [])
            for asset in wallet.assets:
                asset.tags = tags_map.get((self.ASSET_ENTITY_TYPE, asset.id), [])

    async def get(self, id: int) -> Wallet:
        wallet = await self.repo.get(id)
        self._verify(wallet)
        return wallet

    async def get_with_assets(self, id: int) -> Wallet:
        wallet = await self.repo.get_with_assets(id)
        self._verify(wallet)
        return wallet

    async def get_all_with_assets(self) -> list[Wallet]:
        wallets = await self.repo.get_all_by_user_with_assets(self.actor.id)
        await self._bulk_load_tags(wallets)
        return wallets

    async def create(self, data: WalletCreateRequest) -> Wallet:
        await self._validate_unique_name(data.name)
        wallet = await self.repo.create(WalletCreate(**data.model_dump(), user_id=self.actor.id).model_dump())
        await self.session.flush()
        return wallet

    async def update(self, id: int, data: WalletUpdateRequest) -> Wallet:
        wallet = await self.get(id)
        if wallet.is_archived:
            raise ConflictError('Нельзя редактировать архивный кошелёк')
        if data.name != wallet.name:
            await self._validate_unique_name(data.name)
        return await self.repo.update(id, WalletUpdate(**data.model_dump()).model_dump())

    async def delete(self, id: int) -> None:
        wallet = await self.get(id)
        has_txns = await self.transaction_repo.exists_for_wallet(id)
        if has_txns:
            raise ConflictError('Нельзя удалить кошелёк с транзакциями')
        await self.repo.delete(id)

    async def archive(self, id: int) -> None:
        wallet = await self.repo.get_with_assets(id)
        self._verify(wallet)
        await self.repo.update(id, {'is_archived': True})
        for asset in wallet.assets:
            if not asset.is_archived:
                await self.asset_service.archive(asset.id)

    async def unarchive(self, id: int) -> None:
        await self.get(id)
        await self.repo.update(id, {'is_archived': False})

    async def delete_asset(self, wallet_id: int, asset_id: int) -> None:
        await self.get(wallet_id)
        await self.asset_service.delete(asset_id)

    async def archive_asset(self, wallet_id: int, asset_id: int) -> None:
        await self.get(wallet_id)
        await self.asset_service.archive(asset_id)

    async def unarchive_asset(self, wallet_id: int, asset_id: int) -> None:
        await self.get(wallet_id)
        await self.asset_service.unarchive(asset_id)

    async def handle_transaction(self, t: Transaction, *, cancel: bool = False) -> None:
        if not t.wallet_id:
            return
        await self.asset_service.handle_transaction(t, cancel=cancel)

    async def _validate_unique_name(self, name: str) -> None:
        if await self.repo.exists_by_name_and_user(name, self.actor.id):
            raise ConflictError('Кошелек с таким именем уже существует')

    def _verify(self, wallet) -> None:
        if not wallet:
            raise NotFoundError('Кошелек не найден')
        if wallet.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав для получения кошелька')
