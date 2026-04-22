from sqlalchemy import and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from shared.repositories import BaseRepository

from app.models import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    """Репозиторий для работы с транзакциями."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Transaction, session)

    async def get_all_by_ticker_and_portfolio(self, ticker_id: str, portfolio_id: int) -> list[Transaction]:
        """Получить транзакции портфеля по тикеру."""
        condition = or_(
            and_(
                Transaction.ticker_id == ticker_id,
                Transaction.portfolio_id == portfolio_id,
            ),
            and_(
                Transaction.ticker2_id == ticker_id,
                Transaction.portfolio2_id == portfolio_id,
            ),
        )

        return await self.get_all(condition, order=[Transaction.date.desc()])

    async def get_all_by_ticker_and_wallet(self, ticker_id: str, wallet_id: int) -> list[Transaction]:
        """Получить транзакции кошелька по тикеру."""
        condition = or_(
            and_(
                Transaction.ticker_id == ticker_id,
                Transaction.wallet_id == wallet_id,
            ),
            and_(
                Transaction.ticker2_id == ticker_id,
                Transaction.wallet2_id == wallet_id,
            ),
        )

        return await self.get_all(condition, order=[Transaction.date.desc()])
