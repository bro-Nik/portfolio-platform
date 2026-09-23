"""Фильтрация используемых тикеров по рынку.

`get_used_ticker_ids` игнорировал market, поэтому задача цен для stocks-провайдера
запрашивала у него внешние id крипты.
"""

from decimal import Decimal

import pytest

from app.modules.market.models import Ticker
from app.modules.portfolios.models import Portfolio, PortfolioAsset, Wallet, WalletAsset
from app.modules.portfolios.repositories import TickerUsageRepository


@pytest.fixture
async def usage(db_session):
    return TickerUsageRepository(db_session)


async def _seed(db_session, ticker_ids):
    portfolio = Portfolio(name='П', market='crypto', user_id=1)
    wallet = Wallet(name='W', user_id=1)
    db_session.add_all([portfolio, wallet])
    await db_session.flush()
    for ticker_id in ticker_ids:
        db_session.add_all(
            [
                PortfolioAsset(
                    ticker_id=ticker_id,
                    portfolio_id=portfolio.id,
                    user_id=1,
                    quantity=Decimal(1),
                ),
                WalletAsset(
                    ticker_id=ticker_id,
                    wallet_id=wallet.id,
                    user_id=1,
                    quantity=Decimal(1),
                ),
            ]
        )
    await db_session.flush()


@pytest.fixture
async def user(db_session, save):
    from app.modules.auth.models import User

    return await save(db_session, User(email='u@example.com', password_hash='x', is_verified=True))


@pytest.fixture
async def market_tickers(db_session, user):
    rows = [
        Ticker(name='Bitcoin', symbol='BTC', market='crypto', price=0.0),
        Ticker(name='Ether', symbol='ETH', market='crypto', price=0.0),
        Ticker(name='Apple', symbol='AAPL', market='stocks', price=0.0),
        Ticker(name='EUR', symbol='EUR', market='currency', price=0.0),
    ]
    db_session.add_all(rows)
    await db_session.flush()
    return {t.symbol: t.id for t in rows}


class TestGetUsedTickerIds:
    async def test_empty(self, usage):
        assert await usage.get_used_ticker_ids() == []
        assert await usage.get_used_ticker_ids('crypto') == []

    async def test_all_markets(self, usage, db_session, user, market_tickers):
        await _seed(db_session, [market_tickers['BTC'], market_tickers['AAPL'], market_tickers['EUR']])

        result = await usage.get_used_ticker_ids()

        assert set(result) == {market_tickers['BTC'], market_tickers['AAPL'], market_tickers['EUR']}

    async def test_filters_by_market(self, usage, db_session, user, market_tickers):
        await _seed(db_session, [market_tickers['BTC'], market_tickers['AAPL'], market_tickers['EUR']])

        crypto = await usage.get_used_ticker_ids('crypto')
        stocks = await usage.get_used_ticker_ids('stocks')

        assert set(crypto) == {market_tickers['BTC']}
        assert set(stocks) == {market_tickers['AAPL']}

    async def test_unknown_market_is_empty(self, usage, db_session, user, market_tickers):
        await _seed(db_session, [market_tickers['BTC']])

        assert await usage.get_used_ticker_ids('nonexistent') == []
