import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from shared.exceptions import BusinessRuleError, NotFoundError, PermissionDeniedError

from app.models import PortfolioAsset, Transaction, WalletAsset
from app.repositories import TransactionRepository
from app.schemas import (
    Context,
    TransactionCreate,
    TransactionCreateRequest,
    TransactionResponseWithAssets,
    TransactionUpdate,
    TransactionUpdateRequest,
)
from app.services.portfolio import PortfolioService
from app.services.portfolio_asset import PortfolioAssetService
from app.services.wallet import WalletService
from app.services.wallet_asset import WalletAssetService


class TransactionService:
    """Сервис для работы с транзакциями активов портфелей и кошельков."""

    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = TransactionRepository(session)
        self.portfolio_service = PortfolioService(session, ctx)
        self.portfolio_asset_service = PortfolioAssetService(session, ctx)
        self.wallet_service = WalletService(session, ctx)
        self.wallet_asset_service = WalletAssetService(session, ctx)

    async def get(self, id: int) -> Transaction:
        """Получить транзакцию."""
        transaction = await self.repo.get(id)
        self._verify(transaction)
        return transaction

    async def create(self, data: TransactionCreateRequest) -> Transaction:
        """Создание новой транзакции."""
        await self._validate_transaction_data(data)

        transaction_to_db = TransactionCreate(**data.model_dump(exclude_unset=True), user_id=self.actor.id)
        transaction = await self.repo.create(transaction_to_db.model_dump())
        await self.session.flush()

        # Уведомление сервисов о транзакции
        await self._notify_services(transaction)

        return transaction

    async def update(self, id: int, data: TransactionUpdateRequest) -> tuple[Transaction, Transaction]:
        """Обновление транзакции."""
        await self._validate_transaction_data(data)
        old_transaction = await self.get(id)

        # Уведомление сервисов о отмене транзакции
        await self._notify_services(old_transaction, cancel=True)

        transaction_to_db = TransactionUpdate(**data.model_dump(exclude_unset=True))
        updated_transaction = await self.repo.update(old_transaction.id, transaction_to_db.model_dump())

        # Уведомление сервисов о транзакции
        await self._notify_services(updated_transaction)

        return updated_transaction, old_transaction

    async def delete(self, id: int) -> Transaction:
        """Удаление транзакции."""
        transaction = await self.get(id)

        # Уведомление сервисов о отмене транзакции
        await self._notify_services(transaction, cancel=True)

        await self.repo.delete(id)
        return transaction

    async def convert_order_to_transaction(self, id: int) -> tuple[Transaction, Transaction]:
        """Конвертация ордера в транзакцию."""
        await self.get(id)
        update_data = TransactionUpdateRequest(order=False)
        return await self.update(id, update_data)

    async def get_asset_transactions(self, asset: PortfolioAsset | WalletAsset) -> list[Transaction]:
        """Получить транзакции портфеля."""
        if isinstance(asset, PortfolioAsset):
            transactions = await self.repo.get_all_by_ticker_and_portfolio(
                asset.ticker_id,
                asset.portfolio_id,
            )
        else:
            transactions = await self.repo.get_all_by_ticker_and_wallet(
                asset.ticker_id,
                asset.wallet_id,
            )
        return transactions

    async def _validate_transaction_data(self, data: TransactionCreateRequest | TransactionUpdateRequest) -> None:
        if data.type in ('Buy', 'Sell'):
            required = ['portfolio_id', 'wallet_id', 'ticker_id', 'ticker2_id', 'quantity']
            self._validate_required_fields(data, required)

        elif data.type == 'Earning':
            required = ['portfolio_id', 'wallet_id', 'ticker_id', 'quantity']
            self._validate_required_fields(data, required)

        elif data.type in ('TransferIn', 'TransferOut'):
            if data.portfolio_id:
                required = ['portfolio_id', 'portfolio2_id', 'ticker_id', 'quantity']
            else:
                required = ['wallet_id', 'wallet2_id', 'ticker_id', 'quantity']
            self._validate_required_fields(data, required)

        elif data.type in ('Input', 'Output'):
            if data.portfolio_id:
                required = ['portfolio_id', 'ticker_id', 'quantity']
            else:
                required = ['wallet_id', 'ticker_id', 'quantity']
            self._validate_required_fields(data, required)

        else:
            raise BusinessRuleError(f'Неизвестный тип транзакции: {data.type}')

    async def _notify_services(self, t: Transaction, *, cancel: bool = False) -> None:
        await self.portfolio_service.handle_transaction(t, cancel=cancel)
        await self.wallet_service.handle_transaction(t, cancel=cancel)

    @staticmethod
    def _validate_required_fields(
        data: TransactionCreateRequest | TransactionUpdateRequest,
        required_fields: list[str],
    ) -> None:
        missing = [field for field in required_fields if getattr(data, field, None) is None]
        if missing:
            raise BusinessRuleError(f'Отсутствуют обязательные поля: {", ".join(missing)}')

    async def build_response_with_assets(self, *transactions: Transaction) -> TransactionResponseWithAssets:
        portfolio_assets, wallet_assets = await asyncio.gather(
            self.portfolio_asset_service.get_affected(*transactions),
            self.wallet_asset_service.get_affected(*transactions),
        )

        return TransactionResponseWithAssets(
            transaction=transactions[0],
            portfolio_assets=portfolio_assets,
            wallet_assets=wallet_assets,
        )

    def _verify(self, transaction: Transaction) -> None:
        self._check_exists(transaction)
        self._check_permission(transaction)

    def _check_exists(self, transaction: Transaction | None) -> None:
        if not transaction:
            raise NotFoundError('Транзакция не найдена')

    def _check_permission(self, transaction: Transaction) -> None:
        if transaction.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав')
