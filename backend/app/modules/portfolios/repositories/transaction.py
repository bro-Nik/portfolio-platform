from collections.abc import Iterable

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.repositories import BaseRepository
from app.modules.portfolios.models import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Transaction, session)

    async def get_all_by_ticker_and_portfolio(self, ticker_id: int, portfolio_id: int) -> list[Transaction]:
        condition = or_(
            and_(Transaction.ticker_id == ticker_id, Transaction.portfolio_id == portfolio_id),
            and_(Transaction.ticker2_id == ticker_id, Transaction.portfolio2_id == portfolio_id),
        )
        return await self.get_all(condition, order=[Transaction.date.desc()])

    async def get_all_by_ticker_and_wallet(self, ticker_id: int, wallet_id: int) -> list[Transaction]:
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

    async def portfolios_tickers_with_transactions(self, portfolio_tickers: dict[int, list[int]]) -> set[tuple[int, int]]:
        tickers_by_portfolio = {pid: set(tids) for pid, tids in portfolio_tickers.items() if tids}
        if not tickers_by_portfolio:
            return set()
        conditions = []
        for pid, ticker_ids in tickers_by_portfolio.items():
            conditions.extend(
                [
                    and_(Transaction.portfolio_id == pid, Transaction.ticker_id.in_(ticker_ids)),
                    and_(Transaction.portfolio2_id == pid, Transaction.ticker2_id.in_(ticker_ids)),
                    and_(Transaction.portfolio_id == pid, Transaction.ticker2_id.in_(ticker_ids)),
                    and_(Transaction.portfolio2_id == pid, Transaction.ticker_id.in_(ticker_ids)),
                ],
            )
        stmt = select(
            Transaction.portfolio_id,
            Transaction.portfolio2_id,
            Transaction.ticker_id,
            Transaction.ticker2_id,
        ).where(or_(*conditions))
        result = await self._session.execute(stmt)
        return self._collect_portfolio_ticker_pairs(result, tickers_by_portfolio)

    async def wallets_tickers_with_transactions(self, wallet_tickers: dict[int, list[int]]) -> set[tuple[int, int]]:
        tickers_by_wallet = {wid: set(tids) for wid, tids in wallet_tickers.items() if tids}
        if not tickers_by_wallet:
            return set()
        conditions = []
        for wid, ticker_ids in tickers_by_wallet.items():
            conditions.extend(
                [
                    and_(Transaction.wallet_id == wid, Transaction.ticker_id.in_(ticker_ids)),
                    and_(Transaction.wallet2_id == wid, Transaction.ticker2_id.in_(ticker_ids)),
                    and_(Transaction.wallet_id == wid, Transaction.ticker2_id.in_(ticker_ids)),
                    and_(Transaction.wallet2_id == wid, Transaction.ticker_id.in_(ticker_ids)),
                ],
            )
        stmt = select(
            Transaction.wallet_id,
            Transaction.wallet2_id,
            Transaction.ticker_id,
            Transaction.ticker2_id,
        ).where(or_(*conditions))
        result = await self._session.execute(stmt)
        return self._collect_wallet_ticker_pairs(result, tickers_by_wallet)

    @staticmethod
    def _collect_portfolio_ticker_pairs(result: Iterable[tuple[int | None, int | None, int | None, int | None]],
        tickers_by_portfolio: dict[int, set[int]],
    ) -> set[tuple[int, int]]:
        pairs: set[tuple[int, int]] = set()
        for p1, p2, t1, t2 in result:
            for pid, ticker in ((p1, t1), (p2, t2), (p1, t2), (p2, t1)):
                if (
                    pid is not None
                    and ticker is not None
                    and ticker in tickers_by_portfolio.get(pid, ())
                ):
                    pairs.add((pid, ticker))
        return pairs

    @staticmethod
    def _collect_wallet_ticker_pairs(result: Iterable[tuple[int | None, int | None, int | None, int | None]],
        tickers_by_wallet: dict[int, set[int]],
    ) -> set[tuple[int, int]]:
        pairs: set[tuple[int, int]] = set()
        for w1, w2, t1, t2 in result:
            for wid, ticker in ((w1, t1), (w2, t2), (w1, t2), (w2, t1)):
                if (
                    wid is not None
                    and ticker is not None
                    and ticker in tickers_by_wallet.get(wid, ())
                ):
                    pairs.add((wid, ticker))
        return pairs

    async def exists_for_portfolio_ticker(self, portfolio_id: int, ticker_id: int) -> bool:
        condition = or_(
            and_(Transaction.portfolio_id == portfolio_id, Transaction.ticker_id == ticker_id),
            and_(Transaction.portfolio2_id == portfolio_id, Transaction.ticker2_id == ticker_id),
            and_(Transaction.portfolio_id == portfolio_id, Transaction.ticker2_id == ticker_id),
            and_(Transaction.portfolio2_id == portfolio_id, Transaction.ticker_id == ticker_id),
        )
        return await self.exists_by(condition)

    async def exists_for_wallet_ticker(self, wallet_id: int, ticker_id: int) -> bool:
        condition = or_(
            and_(Transaction.wallet_id == wallet_id, Transaction.ticker_id == ticker_id),
            and_(Transaction.wallet2_id == wallet_id, Transaction.ticker2_id == ticker_id),
            and_(Transaction.wallet_id == wallet_id, Transaction.ticker2_id == ticker_id),
            and_(Transaction.wallet2_id == wallet_id, Transaction.ticker_id == ticker_id),
        )
        return await self.exists_by(condition)
