from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions import BusinessRuleError, ConflictError, NotFoundError, PermissionDeniedError

from app.modules.market.repositories import TickerRepository
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
        self.ticker_repo = TickerRepository(session)
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
        self._validate_values(data)
        await self._validate_references(data)
        await self._ensure_not_archived(data)
        t = await self.repo.create(TransactionCreate(**data.model_dump(exclude_unset=True), user_id=self.actor.id).model_dump())
        await self.session.flush()
        await self._notify_services(t)
        await self.session.commit()
        return t

    async def update(self, id: int, data: TransactionUpdateRequest) -> tuple[Transaction, Transaction]:
        self._validate_required(data)
        self._validate_values(data)
        await self._validate_references(data)
        old = await self.get(id)
        await self._ensure_not_archived(old)
        await self._notify_services(old, cancel=True)
        updated = await self.repo.update(old.id, TransactionUpdate(**data.model_dump(exclude_unset=True)).model_dump(exclude_unset=True))
        await self._notify_services(updated)
        await self.session.commit()
        return updated, old

    async def delete(self, id: int) -> Transaction:
        t = await self.get(id)
        await self._notify_services(t, cancel=True)
        await self.repo.delete(id)
        await self.session.commit()
        return t

    async def build_response_with_assets(self, *transactions: Transaction) -> TransactionResponseWithAssets:
        pa = await self.portfolio_asset_service.get_affected(*transactions)
        wa = await self.wallet_asset_service.get_affected(*transactions)
        return TransactionResponseWithAssets(transaction=transactions[0], portfolio_assets=pa, wallet_assets=wa)

    async def _ensure_not_archived(self, obj) -> None:
        portfolio_ids = {obj.portfolio_id, obj.portfolio2_id} - {None}
        for pid in portfolio_ids:
            portfolio = await self.portfolio_service.get(pid)
            if portfolio.is_archived:
                raise ConflictError('Нельзя создавать/изменять/удалять транзакции в архивном портфеле')

        wallet_ids = {obj.wallet_id, obj.wallet2_id} - {None}
        for wid in wallet_ids:
            wallet = await self.wallet_service.get(wid)
            if wallet.is_archived:
                raise ConflictError('Нельзя создавать/изменять/удалять транзакции в архивном кошельке')

    async def _notify_services(self, t: Transaction, *, cancel: bool = False) -> None:
        await self.portfolio_service.handle_transaction(t, cancel=cancel)
        await self.wallet_service.handle_transaction(t, cancel=cancel)

    def _validate_required(self, data) -> None:
        if hasattr(data, 'type') and data.type:
            required_map = {
                ('Buy', 'Sell'): ['portfolio_id', 'wallet_id', 'ticker_id', 'ticker2_id', 'quantity', 'quantity2', 'price'],
                ('Earning',): ['portfolio_id', 'wallet_id', 'ticker_id', 'quantity'],
                ('Input', 'Output'): ['portfolio_id', 'wallet_id', 'ticker_id', 'quantity'],
                ('TransferIn', 'TransferOut'): ['portfolio_id', 'portfolio2_id', 'ticker_id', 'quantity']
                    if getattr(data, 'portfolio_id', None) else ['wallet_id', 'wallet2_id', 'ticker_id', 'quantity'],
            }
            for types, fields in required_map.items():
                if data.type in types:
                    missing = [f for f in fields if getattr(data, f, None) is None]
                    if missing:
                        raise BusinessRuleError(f'Отсутствуют обязательные поля: {", ".join(missing)}')
                    return
            raise BusinessRuleError(f'Неизвестный тип транзакции: {data.type}')

    def _validate_values(self, data) -> None:
        for field in ('quantity', 'quantity2', 'price', 'price_usd'):
            value = getattr(data, field, None)
            if value is not None and Decimal(value) <= 0:
                raise BusinessRuleError(f'Поле {field} должно быть больше нуля')

        ticker_id = getattr(data, 'ticker_id', None)
        ticker2_id = getattr(data, 'ticker2_id', None)
        if ticker_id is not None and ticker2_id is not None and ticker_id == ticker2_id:
            raise BusinessRuleError('Тикеры транзакции должны различаться')

        if hasattr(data, 'type') and data.type in ('TransferIn', 'TransferOut'):
            has_portfolio = data.portfolio_id is not None or data.portfolio2_id is not None
            has_wallet = data.wallet_id is not None or data.wallet2_id is not None
            if has_portfolio and has_wallet:
                raise BusinessRuleError(
                    'Перевод должен быть между двумя портфелями или двумя кошельками',
                )

    async def _validate_references(self, data) -> None:
        ticker_ids = []
        for field in ('ticker_id', 'ticker2_id'):
            value = getattr(data, field, None)
            if value is not None:
                ticker_ids.append(value)
        if not ticker_ids:
            return
        existing = await self.ticker_repo.get_all_by_ids(ticker_ids)
        missing = sorted(set(ticker_ids) - {t.id for t in existing})
        if missing:
            raise BusinessRuleError(f'Тикер не найден: {", ".join(map(str, missing))}')

    def _verify(self, t: Transaction) -> None:
        if not t:
            raise NotFoundError('Транзакция не найдена')
        if t.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав')
