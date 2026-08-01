from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.modules.portfolios.models import (
    Portfolio,
    PortfolioAsset,
    Transaction,
    Wallet,
    WalletAsset,
)


class TestOverviewAPI:
    @pytest.mark.usefixtures('tickers')
    async def test_overview_has_transactions(
        self, client, auth_headers, db_session, user, save,
    ):
        portfolio = await save(
            db_session, Portfolio(name='Основной портфель', market='crypto', user_id=user.id),
        )
        wallet = await save(
            db_session, Wallet(name='Основной кошелек', user_id=user.id),
        )
        transfer_target = await save(
            db_session, Portfolio(name='Получатель', market='crypto', user_id=user.id),
        )
        empty_portfolio = await save(
            db_session, Portfolio(name='Пустой портфель', market='crypto', user_id=user.id),
        )
        empty_wallet = await save(
            db_session, Wallet(name='Пустой кошелек', user_id=user.id),
        )

        def make_portfolio_asset(portfolio_id: int, ticker_id: int) -> PortfolioAsset:
            return PortfolioAsset(
                ticker_id=ticker_id,
                portfolio_id=portfolio_id,
                quantity=Decimal('0.5'),
                buy_orders=Decimal(0),
                sell_orders=Decimal(0),
                amount=Decimal('21500.00'),
                percent=Decimal(100),
                user_id=user.id,
            )

        def make_wallet_asset(wallet_id: int, ticker_id: int) -> WalletAsset:
            return WalletAsset(
                ticker_id=ticker_id,
                wallet_id=wallet_id,
                quantity=Decimal('0.5'),
                buy_orders=Decimal(0),
                sell_orders=Decimal(0),
                user_id=user.id,
            )

        await save(db_session, make_portfolio_asset(portfolio.id, 1))
        await save(db_session, make_portfolio_asset(portfolio.id, 2))
        await save(db_session, make_portfolio_asset(portfolio.id, 5))
        await save(db_session, make_portfolio_asset(empty_portfolio.id, 1))
        await save(db_session, make_portfolio_asset(transfer_target.id, 1))
        await save(db_session, make_portfolio_asset(transfer_target.id, 6))

        await save(db_session, make_wallet_asset(wallet.id, 1))
        await save(db_session, make_wallet_asset(wallet.id, 2))
        await save(db_session, make_wallet_asset(wallet.id, 5))
        await save(db_session, make_wallet_asset(empty_wallet.id, 1))

        buy = Transaction(
            date=datetime.now(UTC),
            ticker_id=1,
            ticker2_id=2,
            quantity=Decimal('1.5'),
            quantity2=Decimal('20000.0'),
            price=Decimal('15000.00'),
            price_usd=Decimal('14900.00'),
            type='Buy',
            portfolio_id=portfolio.id,
            wallet_id=wallet.id,
            user_id=user.id,
        )
        await save(db_session, buy)

        transfer = Transaction(
            date=datetime.now(UTC),
            ticker_id=1,
            quantity=Decimal('1.0'),
            type='TransferOut',
            portfolio_id=portfolio.id,
            portfolio2_id=transfer_target.id,
            user_id=user.id,
        )
        await save(db_session, transfer)

        wallet_transfer = Transaction(
            date=datetime.now(UTC),
            ticker_id=4,
            quantity=Decimal('1.0'),
            type='TransferOut',
            wallet_id=empty_wallet.id,
            wallet2_id=wallet.id,
            user_id=user.id,
        )
        await save(db_session, wallet_transfer)

        response = await client.get('/api/overview', headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        by_id = {p['id']: p for p in data['portfolios']}

        assert by_id[portfolio.id]['has_transactions'] is True
        assets = {a['ticker_id']: a for a in by_id[portfolio.id]['assets']}
        assert assets[1]['has_transactions'] is True
        assert assets[2]['has_transactions'] is True
        assert assets[5]['has_transactions'] is False

        assert by_id[empty_portfolio.id]['has_transactions'] is False
        empty_assets = {a['ticker_id']: a for a in by_id[empty_portfolio.id]['assets']}
        assert empty_assets[1]['has_transactions'] is False

        assert by_id[transfer_target.id]['has_transactions'] is True
        target_assets = {a['ticker_id']: a for a in by_id[transfer_target.id]['assets']}
        assert target_assets[1]['has_transactions'] is True
        assert target_assets[6]['has_transactions'] is False

        wallets_by_id = {w['id']: w for w in data['wallets']}

        assert wallets_by_id[wallet.id]['has_transactions'] is True
        wallet_assets = {a['ticker_id']: a for a in wallets_by_id[wallet.id]['assets']}
        assert wallet_assets[1]['has_transactions'] is True
        assert wallet_assets[2]['has_transactions'] is True
        assert wallet_assets[5]['has_transactions'] is False

        assert wallets_by_id[empty_wallet.id]['has_transactions'] is True
        empty_wallet_assets = {a['ticker_id']: a for a in wallets_by_id[empty_wallet.id]['assets']}
        assert empty_wallet_assets[1]['has_transactions'] is False
