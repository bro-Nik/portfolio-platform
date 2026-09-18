"""Проверки exists-множеств репозитория транзакций.

Логика редукции живёт в SQL (UNION + DISTINCT), поэтому проверяется на реальной
базе, а не на чистой функции: регрессия в редукции иначе проскочила бы в
production, а в тестах на create_all её было бы не видно.
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.modules.portfolios.models import Portfolio, Transaction, Wallet
from app.modules.portfolios.repositories.transaction import TransactionRepository


@pytest.fixture
def repo(db_session):
    return TransactionRepository(db_session)


@pytest.fixture
async def second_portfolio(db_session, user, save):
    return await save(db_session, Portfolio(name='Второй', market='crypto', user_id=user.id))


@pytest.fixture
async def second_wallet(db_session, user, save):
    return await save(db_session, Wallet(name='Второй', user_id=user.id))


def _txn(**kwargs) -> Transaction:
    base = {
        'date': datetime.now(UTC),
        'ticker_id': 1,
        'quantity': Decimal(1),
        'type': 'Buy',
    }
    return Transaction(**{**base, **kwargs})


class TestParentsWithTransactions:
    async def test_empty_input_returns_empty_set(self, repo):
        assert await repo.portfolios_with_transactions([]) == set()

    async def test_no_transactions(self, repo, portfolio, second_portfolio):
        assert await repo.portfolios_with_transactions([portfolio.id, second_portfolio.id]) == set()

    async def test_first_leg(self, repo, portfolio, second_portfolio, user, save):
        await save(repo._session, _txn(portfolio_id=portfolio.id, user_id=user.id))

        result = await repo.portfolios_with_transactions([portfolio.id, second_portfolio.id])

        assert result == {portfolio.id}

    async def test_second_leg(self, repo, portfolio, user, save):
        await save(repo._session, _txn(portfolio2_id=portfolio.id, user_id=user.id))

        assert await repo.portfolios_with_transactions([portfolio.id]) == {portfolio.id}

    async def test_transfer_counts_both_legs_once(
        self,
        repo,
        portfolio,
        second_portfolio,
        user,
        save,
    ):
        await save(
            repo._session,
            _txn(
                portfolio_id=portfolio.id,
                portfolio2_id=second_portfolio.id,
                user_id=user.id,
            ),
        )

        result = await repo.portfolios_with_transactions([portfolio.id, second_portfolio.id])

        assert result == {portfolio.id, second_portfolio.id}

    async def test_ignores_parents_outside_request(self, repo, portfolio, second_portfolio, user, save):
        await save(repo._session, _txn(portfolio_id=second_portfolio.id, user_id=user.id))

        assert await repo.portfolios_with_transactions([portfolio.id]) == set()

    async def test_wallet_variants(self, repo, wallet, second_wallet, user, save):
        await save(
            repo._session,
            _txn(wallet_id=wallet.id, wallet2_id=second_wallet.id, user_id=user.id),
        )

        assert await repo.wallets_with_transactions([wallet.id, second_wallet.id]) == {
            wallet.id,
            second_wallet.id,
        }
        assert await repo.wallets_with_transactions([wallet.id]) == {wallet.id}
        assert await repo.wallets_with_transactions([]) == set()


class TestParentTickerPairsWithTransactions:
    async def test_empty_input(self, repo):
        assert await repo.portfolios_tickers_with_transactions({}) == set()
        assert await repo.portfolios_tickers_with_transactions({1: []}) == set()

    async def test_ticker_in_portfolio(self, repo, portfolio, user, save):
        await save(repo._session, _txn(portfolio_id=portfolio.id, ticker_id=3, user_id=user.id))

        result = await repo.portfolios_tickers_with_transactions({portfolio.id: [3]})

        assert result == {(portfolio.id, 3)}

    async def test_counter_ticker_of_transaction(self, repo, portfolio, user, save):
        await save(
            repo._session,
            _txn(portfolio_id=portfolio.id, ticker_id=1, ticker2_id=4, user_id=user.id),
        )

        result = await repo.portfolios_tickers_with_transactions({portfolio.id: [4]})

        assert result == {(portfolio.id, 4)}

    async def test_transfer_matches_both_legs(
        self,
        repo,
        portfolio,
        second_portfolio,
        user,
        save,
    ):
        await save(
            repo._session,
            _txn(
                portfolio_id=portfolio.id,
                portfolio2_id=second_portfolio.id,
                ticker_id=2,
                ticker2_id=5,
                user_id=user.id,
            ),
        )

        result = await repo.portfolios_tickers_with_transactions(
            {portfolio.id: [2], second_portfolio.id: [5]},
        )

        assert result == {(portfolio.id, 2), (second_portfolio.id, 5)}

    async def test_crossed_legs_of_transfer(self, repo, portfolio, second_portfolio, user, save):
        await save(
            repo._session,
            _txn(
                portfolio_id=portfolio.id,
                portfolio2_id=second_portfolio.id,
                ticker_id=2,
                ticker2_id=5,
                user_id=user.id,
            ),
        )

        result = await repo.portfolios_tickers_with_transactions(
            {portfolio.id: [5], second_portfolio.id: [2]},
        )

        assert result == {(portfolio.id, 5), (second_portfolio.id, 2)}

    async def test_ignores_tickers_not_requested(self, repo, portfolio, user, save):
        await save(
            repo._session,
            _txn(portfolio_id=portfolio.id, ticker_id=1, ticker2_id=4, user_id=user.id),
        )

        result = await repo.portfolios_tickers_with_transactions({portfolio.id: [1]})

        assert result == {(portfolio.id, 1)}

    async def test_ignores_parents_outside_request(self, repo, portfolio, second_portfolio, user, save):
        await save(repo._session, _txn(portfolio_id=second_portfolio.id, ticker_id=3, user_id=user.id))

        assert await repo.portfolios_tickers_with_transactions({portfolio.id: [3]}) == set()

    async def test_wallet_variants(self, repo, wallet, user, save):
        await save(
            repo._session,
            _txn(wallet_id=wallet.id, ticker_id=6, ticker2_id=7, user_id=user.id),
        )

        result = await repo.wallets_tickers_with_transactions({wallet.id: [7]})

        assert result == {(wallet.id, 7)}


class TestQueryShape:
    """Редукция обязана оставаться в SQL, а не возвращаться в Python."""

    def _sql(self, stmt) -> str:
        return str(stmt.compile(compile_kwargs={'literal_binds': False}))

    def test_parents_use_union_distinct(self, repo):
        stmt = repo._unioned_ids(
            [
                (Transaction.portfolio_id, None, [1, 2]),
                (Transaction.portfolio2_id, None, [1, 2]),
            ],
        )

        sql = self._sql(stmt)

        assert 'UNION' in sql
        assert 'DISTINCT' in sql

    def test_pairs_use_union_distinct(self, repo):
        stmt = repo._unioned_pairs(
            [
                (Transaction.portfolio_id, Transaction.ticker_id),
                (Transaction.portfolio2_id, Transaction.ticker2_id),
            ],
            [1, 2],
            [10, 20],
        )

        sql = self._sql(stmt)

        assert 'UNION' in sql
        assert 'DISTINCT' in sql

    def test_pairs_do_not_scale_with_portfolio_count(self, repo):
        # Прежний вариант строил 4*P дизъюнктов; теперь их ровно четыре.
        stmt = repo._unioned_pairs(
            [
                (Transaction.portfolio_id, Transaction.ticker_id),
                (Transaction.portfolio_id, Transaction.ticker2_id),
                (Transaction.portfolio2_id, Transaction.ticker_id),
                (Transaction.portfolio2_id, Transaction.ticker2_id),
            ],
            list(range(1, 51)),
            [10, 20],
        )

        assert self._sql(stmt).count('UNION') == 3
