from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository

from app.modules.portfolios.models import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Transaction, session)

    async def get_all_by_ticker_and_portfolio(self, ticker_id: str, portfolio_id: int) -> list[Transaction]:
        condition = or_(
            and_(Transaction.ticker_id == ticker_id, Transaction.portfolio_id == portfolio_id),
            and_(Transaction.ticker2_id == ticker_id, Transaction.portfolio2_id == portfolio_id),
        )
        return await self.get_all(condition, order=[Transaction.date.desc()])

    async def get_all_by_ticker_and_wallet(self, ticker_id: str, wallet_id: int) -> list[Transaction]:
        condition = or_(
            and_(Transaction.ticker_id == ticker_id, Transaction.wallet_id == wallet_id),
            and_(Transaction.ticker2_id == ticker_id, Transaction.wallet2_id == wallet_id),
        )
        return await self.get_all(condition, order=[Transaction.date.desc()])

    async def exists_for_portfolio(self, portfolio_id: int) -> bool:
        condition = or_(
            Transaction.portfolio_id == portfolio_id,
            Transaction.portfolio2_id == portfolio_id,
        )
        return await self.exists_by(condition)

    async def exists_for_wallet(self, wallet_id: int) -> bool:
        condition = or_(
            Transaction.wallet_id == wallet_id,
            Transaction.wallet2_id == wallet_id,
        )
        return await self.exists_by(condition)

    async def portfolios_with_transactions(self, portfolio_ids: list[int]) -> set[int]:
        if not portfolio_ids:
            return set()
        condition = or_(
            Transaction.portfolio_id.in_(portfolio_ids),
            Transaction.portfolio2_id.in_(portfolio_ids),
        )
        stmt = select(Transaction.portfolio_id, Transaction.portfolio2_id).where(condition)
        result = await self._session.execute(stmt)
        ids = set()
        for row in result:
            if row[0] is not None:
                ids.add(row[0])
            if row[1] is not None:
                ids.add(row[1])
        return ids

    async def wallets_with_transactions(self, wallet_ids: list[int]) -> set[int]:
        if not wallet_ids:
            return set()
        condition = or_(
            Transaction.wallet_id.in_(wallet_ids),
            Transaction.wallet2_id.in_(wallet_ids),
        )
        stmt = select(Transaction.wallet_id, Transaction.wallet2_id).where(condition)
        result = await self._session.execute(stmt)
        ids = set()
        for row in result:
            if row[0] is not None:
                ids.add(row[0])
            if row[1] is not None:
                ids.add(row[1])
        return ids

    async def portfolio_tickers_with_transactions(self, portfolio_id: int, ticker_ids: list[str]) -> set[str]:
        if not ticker_ids:
            return set()
        condition = or_(
            and_(Transaction.portfolio_id == portfolio_id, Transaction.ticker_id.in_(ticker_ids)),
            and_(Transaction.portfolio2_id == portfolio_id, Transaction.ticker2_id.in_(ticker_ids)),
            and_(Transaction.portfolio_id == portfolio_id, Transaction.ticker2_id.in_(ticker_ids)),
            and_(Transaction.portfolio2_id == portfolio_id, Transaction.ticker_id.in_(ticker_ids)),
        )
        stmt = select(Transaction.ticker_id, Transaction.ticker2_id).where(condition)
        result = await self._session.execute(stmt)
        tickers = set()
        for row in result:
            if row[0] is not None:
                tickers.add(row[0])
            if row[1] is not None:
                tickers.add(row[1])
        return tickers

    async def wallet_tickers_with_transactions(self, wallet_id: int, ticker_ids: list[str]) -> set[str]:
        if not ticker_ids:
            return set()
        condition = or_(
            and_(Transaction.wallet_id == wallet_id, Transaction.ticker_id.in_(ticker_ids)),
            and_(Transaction.wallet2_id == wallet_id, Transaction.ticker2_id.in_(ticker_ids)),
            and_(Transaction.wallet_id == wallet_id, Transaction.ticker2_id.in_(ticker_ids)),
            and_(Transaction.wallet2_id == wallet_id, Transaction.ticker_id.in_(ticker_ids)),
        )
        stmt = select(Transaction.ticker_id, Transaction.ticker2_id).where(condition)
        result = await self._session.execute(stmt)
        tickers = set()
        for row in result:
            if row[0] is not None:
                tickers.add(row[0])
            if row[1] is not None:
                tickers.add(row[1])
        return tickers

    async def exists_for_portfolio_ticker(self, portfolio_id: int, ticker: str) -> bool:
        condition = or_(
            and_(Transaction.portfolio_id == portfolio_id, Transaction.ticker_id == ticker),
            and_(Transaction.portfolio2_id == portfolio_id, Transaction.ticker2_id == ticker),
            and_(Transaction.portfolio_id == portfolio_id, Transaction.ticker2_id == ticker),
            and_(Transaction.portfolio2_id == portfolio_id, Transaction.ticker_id == ticker),
        )
        return await self.exists_by(condition)

    async def exists_for_wallet_ticker(self, wallet_id: int, ticker: str) -> bool:
        condition = or_(
            and_(Transaction.wallet_id == wallet_id, Transaction.ticker_id == ticker),
            and_(Transaction.wallet2_id == wallet_id, Transaction.ticker2_id == ticker),
            and_(Transaction.wallet_id == wallet_id, Transaction.ticker2_id == ticker),
            and_(Transaction.wallet2_id == wallet_id, Transaction.ticker_id == ticker),
        )
        return await self.exists_by(condition)
