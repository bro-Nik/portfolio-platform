import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BusinessRuleError, NotFoundError, PermissionDeniedError

from app.modules.portfolios.models import Transaction
from app.modules.portfolios.repositories import TransactionRepository
from app.modules.portfolios.schemas import (
    TransactionCreate, TransactionCreateRequest,
    TransactionResponseWithAssets, TransactionUpdate, TransactionUpdateRequest,
)
from app.modules.portfolios.services.portfolio import PortfolioService
from app.modules.portfolios.services.portfolio_asset import PortfolioAssetService
from app.modules.portfolios.services.wallet import WalletService
from app.modules.portfolios.services.wallet_asset import WalletAssetService
from app.common.schemas import Context


class TransactionService:
    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = TransactionRepository(session)
        self.portfolio_service = PortfolioService(session, ctx)
        self.portfolio_asset_service = PortfolioAssetService(ctx, session)
        self.wallet_service = WalletService(session, ctx)
        self.wallet_asset_service = WalletAssetService(ctx, session)

    async def get(self, id: int) -> Transaction:
        t = await self.repo.get(id)
        self._verify(t)
        return t

    async def create(self, data: TransactionCreateRequest) -> Transaction:
        self._validate_required(data)
        t = await self.repo.create(TransactionCreate(**data.model_dump(exclude_unset=True), user_id=self.actor.id).model_dump())
        await self.session.flush()
        await self._notify_services(t)
        return t

    async def update(self, id: int, data: TransactionUpdateRequest) -> tuple[Transaction, Transaction]:
        self._validate_required(data)
        old = await self.get(id)
        await self._notify_services(old, cancel=True)
        updated = await self.repo.update(old.id, TransactionUpdate(**data.model_dump(exclude_unset=True)).model_dump())
        await self._notify_services(updated)
        return updated, old

    async def delete(self, id: int) -> Transaction:
        t = await self.get(id)
        await self._notify_services(t, cancel=True)
        await self.repo.delete(id)
        return t

    async def build_response_with_assets(self, *transactions: Transaction) -> TransactionResponseWithAssets:
        pa, wa = await asyncio.gather(
            self.portfolio_asset_service.get_affected(*transactions),
            self.wallet_asset_service.get_affected(*transactions),
        )
        return TransactionResponseWithAssets(transaction=transactions[0], portfolio_assets=pa, wallet_assets=wa)

    async def _notify_services(self, t: Transaction, *, cancel: bool = False) -> None:
        await self.portfolio_service.handle_transaction(t, cancel=cancel)
        await self.wallet_service.handle_transaction(t, cancel=cancel)

    def _validate_required(self, data) -> None:
        if hasattr(data, 'type') and data.type:
            required_map = {
                ('Buy', 'Sell'): ['portfolio_id', 'wallet_id', 'ticker_id', 'ticker2_id', 'quantity'],
                ('Earning',): ['portfolio_id', 'wallet_id', 'ticker_id', 'quantity'],
                ('TransferIn', 'TransferOut'): ['portfolio_id', 'portfolio2_id', 'ticker_id', 'quantity']
                    if getattr(data, 'portfolio_id', None) else ['wallet_id', 'wallet2_id', 'ticker_id', 'quantity'],
                ('Input', 'Output'): ['portfolio_id', 'ticker_id', 'quantity']
                    if getattr(data, 'portfolio_id', None) else ['wallet_id', 'ticker_id', 'quantity'],
            }
            for types, fields in required_map.items():
                if data.type in types:
                    missing = [f for f in fields if getattr(data, f, None) is None]
                    if missing:
                        raise BusinessRuleError(f'Отсутствуют обязательные поля: {", ".join(missing)}')
                    return
            raise BusinessRuleError(f'Неизвестный тип транзакции: {data.type}')

    def _verify(self, t: Transaction) -> None:
        if not t:
            raise NotFoundError('Транзакция не найдена')
        if t.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав')
