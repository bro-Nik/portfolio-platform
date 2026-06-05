import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import ConflictError, NotFoundError, PermissionDeniedError

from app.models import Transaction, Wallet
from app.repositories import TaggableRepository, WalletRepository
from app.schemas import (
    Context,
    WalletCreate,
    WalletCreateRequest,
    WalletUpdate,
    WalletUpdateRequest,
)
from app.services.wallet_asset import WalletAssetService


class WalletService:
    """Сервис для работы с кошельками пользователей."""

    ENTITY_TYPE = 'wallet'
    ASSET_ENTITY_TYPE = 'wallet_asset'

    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = WalletRepository(session)
        self.asset_service = WalletAssetService(session, ctx)
        self.taggable_repo = TaggableRepository(session)

    async def _bulk_load_tags(self, wallets: list[Wallet]) -> None:
        items: list[tuple[str, int]] = []
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
        """Получить кошелек пользователя."""
        wallet = await self.repo.get(id)
        self._verify(wallet)
        return wallet

    async def get_with_assets(self, id: int) -> Wallet:
        """Получить кошелек пользователя с активами."""
        wallet = await self.repo.get_with_assets(id)
        self._verify(wallet)
        return wallet

    async def get_all_with_assets(self) -> list[Wallet]:
        """Получить все кошельки пользователя с активами."""
        wallets = await self.repo.get_all_by_user_with_assets(self.actor.id)
        await self._bulk_load_tags(wallets)
        return wallets

    async def create(self, data: WalletCreateRequest) -> Wallet:
        """Создать кошелек для пользователя."""
        await self._validate_create_data(data)

        wallet_to_db = WalletCreate(**data.model_dump(), user_id=self.actor.id)
        wallet = await self.repo.create(wallet_to_db.model_dump())
        await self.session.flush()
        return wallet

    async def update(self, id: int, data: WalletUpdateRequest) -> Wallet:
        """Обновить кошелек пользователя."""
        wallet = await self.get(id)
        await self._validate_update_data(data, wallet)

        wallet_to_db = WalletUpdate(**data.model_dump())
        return await self.repo.update(id, wallet_to_db.model_dump())

    async def delete(self, id: int) -> None:
        """Удалить кошелек пользователя."""
        await self.get(id)
        await self.repo.delete(id)

    async def handle_transaction(self, t: Transaction, *, cancel: bool = False) -> None:
        """Обработка транзакции."""
        if not t.wallet_id:
            return

        if t.type in ('Buy', 'Sell'):
            await self._handle_trade(t)
        elif t.type == 'Earning':
            await self._handle_earning(t)
        elif t.type in ('TransferIn', 'TransferOut'):
            await self._handle_transfer(t)
        elif t.type in ('Input', 'Output'):
            await self._handle_input_output(t)

        # Уведомление сервиса актива о новой транзакции
        await self.asset_service.handle_transaction(t, cancel=cancel)

    async def _validate_create_data(self, data: WalletCreateRequest) -> None:
        await self._validate_unique_name(data.name)

    async def _validate_update_data(self, data: WalletUpdateRequest, wallet: Wallet) -> None:
        if data.name != wallet.name:
            await self._validate_unique_name(data.name)

    async def _validate_unique_name(self, name: str) -> None:
        if await self.repo.exists_by_name_and_user(name, self.actor.id):
            raise ConflictError('Кошелек с таким именем уже существует')

    async def _validate_wallets(self, *wallet_ids: int | None) -> None:
        if ids := [id_ for id_ in wallet_ids if id_ is not None]:
            await asyncio.gather(*[self.get(id_) for id_ in ids])

    async def _handle_trade(self, t: Transaction) -> None:
        await self._validate_wallets(t.wallet_id)

    async def _handle_earning(self, t: Transaction) -> None:
        await self._validate_wallets(t.wallet_id)

    async def _handle_transfer(self, t: Transaction) -> None:
        await self._validate_wallets(t.wallet_id, t.wallet2_id)

    async def _handle_input_output(self, t: Transaction) -> None:
        await self._validate_wallets(t.wallet_id)

    def _verify(self, wallet: Wallet | None) -> None:
        self._check_exists(wallet)
        self._check_permission(wallet)

    def _check_exists(self, wallet: Wallet | None) -> None:
        if not wallet:
            raise NotFoundError('Кошелек не найден')

    def _check_permission(self, wallet: Wallet) -> None:
        if wallet.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав для получения кошелька')
