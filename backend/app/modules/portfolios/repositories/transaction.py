from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from app.common.repositories import BaseRepository
from app.modules.portfolios.models import Transaction


class TransactionRepository(BaseRepository[Transaction]):
    """Доступ к транзакциям.

    Проверки «есть ли транзакции» возвращают логические множества идентификаторов,
    поэтому редукция выполняется в SQL (UNION + DISTINCT), а не в Python: иначе
    каждый запрос тащил в память по строке на каждую транзакцию пользователя,
    чтобы получить несколько булевых флагов.
    """

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Transaction, session)

    async def get_all_by_ticker_and_portfolio(self, ticker_id: int, portfolio_id: int) -> list[Transaction]:
        condition = or_(
            and_(Transaction.ticker_id == ticker_id, Transaction.portfolio_id == portfolio_id),
            and_(Transaction.ticker2_id == ticker_id, Transaction.portfolio_id == portfolio_id),
            and_(Transaction.ticker_id == ticker_id, Transaction.portfolio2_id == portfolio_id),
            and_(Transaction.ticker2_id == ticker_id, Transaction.portfolio2_id == portfolio_id),
        )
        return await self.get_all(condition, order=[Transaction.date.desc()])

    async def get_all_by_ticker_and_wallet(self, ticker_id: int, wallet_id: int) -> list[Transaction]:
        condition = or_(
            and_(Transaction.ticker_id == ticker_id, Transaction.wallet_id == wallet_id),
            and_(Transaction.ticker2_id == ticker_id, Transaction.wallet_id == wallet_id),
            and_(Transaction.ticker_id == ticker_id, Transaction.wallet2_id == wallet_id),
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
        stmt = self._unioned_ids(
            [
                (Transaction.portfolio_id, Transaction.portfolio_id, portfolio_ids),
                (Transaction.portfolio2_id, Transaction.portfolio2_id, portfolio_ids),
            ],
        )
        if stmt is None:
            return set()
        result = await self._session.execute(stmt)
        return set(result.scalars())

    async def wallets_with_transactions(self, wallet_ids: list[int]) -> set[int]:
        stmt = self._unioned_ids(
            [
                (Transaction.wallet_id, Transaction.wallet_id, wallet_ids),
                (Transaction.wallet2_id, Transaction.wallet2_id, wallet_ids),
            ],
        )
        if stmt is None:
            return set()
        result = await self._session.execute(stmt)
        return set(result.scalars())

    async def portfolios_tickers_with_transactions(
        self,
        portfolio_tickers: dict[int, list[int]],
    ) -> set[tuple[int, int]]:
        return await self._parent_ticker_pairs(
            portfolio_tickers,
            [
                (Transaction.portfolio_id, Transaction.ticker_id),
                (Transaction.portfolio_id, Transaction.ticker2_id),
                (Transaction.portfolio2_id, Transaction.ticker_id),
                (Transaction.portfolio2_id, Transaction.ticker2_id),
            ],
        )

    async def wallets_tickers_with_transactions(self, wallet_tickers: dict[int, list[int]]) -> set[tuple[int, int]]:
        return await self._parent_ticker_pairs(
            wallet_tickers,
            [
                (Transaction.wallet_id, Transaction.ticker_id),
                (Transaction.wallet_id, Transaction.ticker2_id),
                (Transaction.wallet2_id, Transaction.ticker_id),
                (Transaction.wallet2_id, Transaction.ticker2_id),
            ],
        )

    async def _parent_ticker_pairs(
        self,
        parent_tickers: dict[int, list[int]],
        branches: list[tuple[object, object]],
    ) -> set[tuple[int, int]]:
        """Пары (родитель, тикер), для которых есть транзакция.

        SQL отдаёт объединение четырёх ветвей по всем запрошенным тикерам, а
        принадлежность тикера конкретному родителю проверяется здесь: в SQL такая
        проверка стоила бы 4*P дизъюнктов. Строк на выходе — не больше, чем
        уникальных пар, то есть перестаёт зависеть от числа транзакций.
        """
        tickers_by_parent = {pid: set(tids) for pid, tids in parent_tickers.items() if tids}
        if not tickers_by_parent:
            return set()
        ticker_ids = sorted({tid for tids in tickers_by_parent.values() for tid in tids})
        stmt = self._unioned_pairs(branches, list(tickers_by_parent), ticker_ids)
        result = await self._session.execute(stmt)
        return {(parent, ticker) for parent, ticker in result.all() if ticker in tickers_by_parent.get(parent, ())}

    @staticmethod
    def _unioned_ids(branches: list[tuple[object, object, list[int]]]) -> Select | None:
        """UNION DISTINCT одиночных идентификаторов: возвращает не больше, чем их число."""
        if not branches or not branches[0][2]:
            return None
        selects = [select(column).where(column.in_(ids)).distinct() for column, _other, ids in branches]
        return selects[0].union(*selects[1:]) if len(selects) > 1 else selects[0]

    @staticmethod
    def _unioned_pairs(
        branches: list[tuple[object, object]],
        parent_ids: list[int],
        ticker_ids: list[int],
    ) -> Select:
        """UNION DISTINCT пар (родитель, тикер) по четырём сочетаниям колонок.

        Каждая ветвь использует два индекса (по родителю и по тикеру), тогда как
        прежний вариант строил 4*P дизъюнктов и выбирал четыре колонки из всех
        совпавших строк, разворачивая декартово произведение уже в Python.
        """
        selects = [
            select(parent, ticker).where(parent.in_(parent_ids), ticker.in_(ticker_ids)).distinct()
            for parent, ticker in branches
        ]
        return selects[0].union(*selects[1:])

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
