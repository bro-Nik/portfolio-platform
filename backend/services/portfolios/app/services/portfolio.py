import asyncio

from shared.exceptions import ConflictError, NotFoundError, PermissionDeniedError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Portfolio, Transaction
from app.repositories import PortfolioRepository
from app.schemas import (
    Context,
    PortfolioAssetCreateRequest,
    PortfolioCreate,
    PortfolioCreateRequest,
    PortfolioUpdate,
    PortfolioUpdateRequest,
)
from app.services.portfolio_asset import PortfolioAssetService


class PortfolioService:
    """Сервис для работы с портфелями пользователей."""

    def __init__(self, session: AsyncSession, ctx: Context) -> None:
        self.ctx = ctx
        self.actor = ctx.actor
        self.session = session
        self.repo = PortfolioRepository(session)
        self.asset_service = PortfolioAssetService(session, ctx)

    async def get(self, id: int) -> Portfolio:
        """Получить портфель пользователя."""
        portfolio = await self.repo.get(id)
        self._verify(portfolio)
        return portfolio

    async def get_with_assets(self, id: int) -> Portfolio:
        """Получить портфель пользователя с активами."""
        portfolio = await self.repo.get_with_assets(id)
        self._verify(portfolio)
        return portfolio

    async def get_many_with_assets(self) -> list[Portfolio]:
        """Получить все портфели пользователя с активами."""
        return await self.repo.get_many_by_user_with_assets(self.actor.id)

    async def create(self, data: PortfolioCreateRequest) -> Portfolio:
        """Создать портфель для пользователя."""
        await self._validate_create_data(data)

        portfolio_to_db = PortfolioCreate(**data.model_dump(), user_id=self.actor.id)
        portfolio = await self.repo.create(portfolio_to_db)
        await self.session.flush()
        return portfolio

    async def update(self, id: int, data: PortfolioUpdateRequest) -> Portfolio:
        """Обновить портфель пользователя."""
        portfolio = await self.get(id)
        await self._validate_update_data(data, portfolio)

        portfolio_to_db = PortfolioUpdate(**data.model_dump())
        return await self.repo.update(id, portfolio_to_db)

    async def delete(self, id: int) -> None:
        """Удалить портфель пользователя."""
        await self.get(id)
        await self.repo.delete(id)

    async def add_asset(self, id: int, data: PortfolioAssetCreateRequest) -> None:
        """Добавить актив в портфель пользователя."""
        await self.get(id)
        await self.asset_service.create(data)

    async def delete_asset(self, id: int, asset_id: int) -> None:
        """Удалить актив из портфеля пользователя."""
        await self.get(id)
        await self.asset_service.delete(asset_id)

    async def handle_transaction(self, t: Transaction, *, cancel: bool = False) -> None:
        """Обработка транзакции."""
        if not t.portfolio_id:
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

    async def _validate_create_data(self, data: PortfolioCreateRequest) -> None:
        await self._validate_unique_name(data.name)

    async def _validate_update_data(self, data: PortfolioUpdateRequest, portfolio: Portfolio) -> None:
        if data.name != portfolio.name:
            await self._validate_unique_name(data.name)

    async def _validate_unique_name(self, name: str) -> None:
        if await self.repo.exists_by_name_and_user(name, self.actor.id):
            raise ConflictError('Портфель с таким именем уже существует')

    async def _validate_portfolios(self, *portfolio_ids: int | None) -> None:
        if ids := [id for id in portfolio_ids if id is not None]:
            await asyncio.gather(*[self.get(id) for id in ids])

    async def _handle_trade(self, t: Transaction) -> None:
        await self._validate_portfolios(t.portfolio_id)

    async def _handle_earning(self, t: Transaction) -> None:
        await self._validate_portfolios(t.portfolio_id)

    async def _handle_transfer(self, t: Transaction) -> None:
        await self._validate_portfolios(t.portfolio_id, t.portfolio2_id)

    async def _handle_input_output(self, t: Transaction) -> None:
        await self._validate_portfolios(t.portfolio_id)

    def _verify(self, portfolio: Portfolio) -> None:
        self._check_exists(portfolio)
        self._check_permission(portfolio)

    def _check_exists(self, portfolio: Portfolio | None) -> None:
        if not portfolio:
            raise NotFoundError('Портфель не найден')

    def _check_permission(self, portfolio: Portfolio) -> None:
        if portfolio.user_id != self.actor.id:
            raise PermissionDeniedError('Недостаточно прав для получения портфеля')
