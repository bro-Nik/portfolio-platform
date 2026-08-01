from app.modules.portfolios.repositories.transaction import TransactionRepository


class TestCollectPortfolioTickerPairs:
    def test_ticker_in_portfolio(self):
        result = [(1, None, 10, None)]
        pairs = TransactionRepository._collect_portfolio_ticker_pairs(result, {1: {10}})
        assert pairs == {(1, 10)}

    def test_ticker2_side_of_transaction(self):
        result = [(1, None, 10, 20)]
        pairs = TransactionRepository._collect_portfolio_ticker_pairs(result, {1: {20}})
        assert pairs == {(1, 20)}

    def test_transfer_between_portfolios(self):
        result = [(1, 2, 10, 20)]
        pairs = TransactionRepository._collect_portfolio_ticker_pairs(result, {1: {10}, 2: {20}})
        assert pairs == {(1, 10), (2, 20)}

    def test_crossed_legs_of_transfer(self):
        result = [(1, 2, 10, 20)]
        pairs = TransactionRepository._collect_portfolio_ticker_pairs(result, {1: {20}, 2: {10}})
        assert pairs == {(1, 20), (2, 10)}

    def test_ignores_ticker_not_held_by_portfolio(self):
        result = [(1, None, 10, None)]
        pairs = TransactionRepository._collect_portfolio_ticker_pairs(result, {1: {99}})
        assert pairs == set()

    def test_ignores_other_portfolio(self):
        result = [(1, None, 10, None)]
        pairs = TransactionRepository._collect_portfolio_ticker_pairs(result, {2: {10}})
        assert pairs == set()

    def test_ignores_null_columns(self):
        result = [(None, None, None, None)]
        pairs = TransactionRepository._collect_portfolio_ticker_pairs(result, {1: {10}})
        assert pairs == set()

    def test_ignores_tickers_not_requested(self):
        result = [(1, None, 10, 20)]
        pairs = TransactionRepository._collect_portfolio_ticker_pairs(result, {1: {10}})
        assert pairs == {(1, 10)}


class TestCollectWalletTickerPairs:
    def test_ticker_in_wallet(self):
        result = [(1, None, 10, None)]
        pairs = TransactionRepository._collect_wallet_ticker_pairs(result, {1: {10}})
        assert pairs == {(1, 10)}

    def test_receiving_wallet_of_transfer(self):
        result = [(1, 2, 10, None)]
        pairs = TransactionRepository._collect_wallet_ticker_pairs(result, {2: {10}})
        assert pairs == {(2, 10)}

    def test_wallet_holds_counter_ticker(self):
        result = [(1, None, 10, 20)]
        pairs = TransactionRepository._collect_wallet_ticker_pairs(result, {1: {20}})
        assert pairs == {(1, 20)}

    def test_isolation_between_wallets(self):
        result = [(1, None, 10, None)]
        pairs = TransactionRepository._collect_wallet_ticker_pairs(result, {2: {10}})
        assert pairs == set()
