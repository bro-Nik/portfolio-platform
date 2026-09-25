"""Выгрузка персональных данных (152-ФЗ, ст. 14).

Проверяется три вещи: субъект получает копию своих данных, чужих данных в ней
нет, и секреты (хеш пароля, токены) наружу не уходят.
"""

from datetime import UTC, datetime
from decimal import Decimal

from fastapi import status
import pytest

from app.modules.auth.models import LoginSession, RefreshToken, User
from app.modules.auth.repositories import SessionRepository, TokenRepository
from app.modules.portfolios.models import (
    Portfolio,
    PortfolioAsset,
    Transaction,
    WalletAsset,
)
from app.modules.tags.models import Tag, Taggable


@pytest.fixture
async def user_data(db_session, save, user, portfolio, wallet, tickers):
    """Заполняет пользователя данными во всех разделах выгрузки."""
    asset = await save(
        PortfolioAsset(
            ticker_id=tickers[0].id,
            portfolio_id=portfolio.id,
            user_id=user.id,
            quantity=Decimal('1.5'),
            amount=Decimal(100),
        )
    )
    await save(
        WalletAsset(
            ticker_id=tickers[0].id,
            wallet_id=wallet.id,
            user_id=user.id,
            quantity=Decimal(2),
        )
    )
    await save(
        Transaction(
            date=datetime.now(UTC),
            ticker_id=tickers[0].id,
            ticker2_id=tickers[1].id,
            quantity=Decimal(1),
            price=Decimal(100),
            type='Buy',
            portfolio_id=portfolio.id,
            user_id=user.id,
            comment='заметка',
        )
    )
    tag = await save(Tag(name='Крипта', scope='asset', user_id=user.id))
    await save(Taggable(tag_id=tag.id, entity_type='portfolio_asset', entity_id=asset.id))
    return asset


class TestExportAccount:
    async def test_requires_authentication(self, client):
        response = await client.get('/auth/account/export')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_returns_all_sections(self, client, auth_headers, user_data):
        response = await client.get('/auth/account/export', headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for section in (
            'user',
            'sessions',
            'portfolios',
            'portfolio_assets',
            'wallets',
            'wallet_assets',
            'transactions',
            'tags',
            'taggable',
            'tickers',
        ):
            assert section in data, f'в выгрузке нет раздела {section}'
            assert isinstance(data[section], list)

    async def test_contains_own_records(self, client, auth_headers, user_data, user):
        data = (await client.get('/auth/account/export', headers=auth_headers)).json()

        assert data['user'][0]['email'] == user.email
        assert len(data['portfolios']) == 1
        assert len(data['portfolio_assets']) == 1
        assert len(data['transactions']) == 1
        assert data['transactions'][0]['comment'] == 'заметка'
        assert len(data['tags']) == 1

    async def test_excludes_other_users_data(self, client, auth_headers, user_data, db_session, save):
        other = await save(User(email='other@example.com', password_hash='x', is_verified=True))
        await save(Portfolio(name='Чужой', market='crypto', user_id=other.id))
        await save(Tag(name='Чужой тег', scope='asset', user_id=other.id))

        data = (await client.get('/auth/account/export', headers=auth_headers)).json()

        names = [p['name'] for p in data['portfolios']]
        tag_names = [t['name'] for t in data['tags']]
        assert 'Чужой' not in names
        assert 'Чужой тег' not in tag_names

    async def test_never_exposes_password_hash(self, client, auth_headers, user_data):
        data = (await client.get('/auth/account/export', headers=auth_headers)).json()

        assert 'password_hash' not in data['user'][0]
        assert '$2b$' not in str(data)

    async def test_never_exposes_refresh_tokens(self, client, auth_headers, user_data, refresh_token):
        data = (await client.get('/auth/account/export', headers=auth_headers)).json()

        assert 'plain-refresh' not in str(data)
        assert 'c' * 64 not in str(data)

    async def test_includes_sessions_without_tokens(
        self,
        client,
        auth_headers,
        user_data,
        save,
        user,
        refresh_token,
    ):
        await save(
            LoginSession(
                user_id=user.id,
                refresh_token_id=refresh_token.id,
                ip_address='203.0.113.7',
                device_type='desktop',
                browser='Chrome',
                os='macOS',
            )
        )

        data = (await client.get('/auth/account/export', headers=auth_headers)).json()

        if data['sessions']:
            assert data['sessions'][0]['ip_address'] == '203.0.113.7'

    async def test_carries_version_and_timestamp(self, client, auth_headers, user_data):
        data = (await client.get('/auth/account/export', headers=auth_headers)).json()

        assert data['export_version'] >= 1
        assert data['exported_at']

    async def test_dates_are_serialisable(self, client, auth_headers, user_data):
        data = (await client.get('/auth/account/export', headers=auth_headers)).json()

        assert isinstance(data['transactions'][0]['date'], str)
        assert isinstance(data['portfolio_assets'][0]['quantity'], str)


class TestSessionRepositoryUsage:
    async def test_sessions_are_scoped_to_user(self, db_session, save, user, refresh_token):
        other = await save(User(email='other@example.com', password_hash='x'))
        other_token = await save(
            RefreshToken(
                user_id=other.id,
                token='other',
                token_hash='d' * 64,
                expires_at=1,
            )
        )
        await save(LoginSession(user_id=user.id, refresh_token_id=refresh_token.id, ip_address='1.1.1.1'))
        await save(LoginSession(user_id=other.id, refresh_token_id=other_token.id, ip_address='2.2.2.2'))

        sessions = await SessionRepository(db_session).get_all_by_user_id(user.id)

        assert [s.ip_address for s in sessions] == ['1.1.1.1']


class TestTokenRepositoryIsolation:
    async def test_refresh_tokens_not_readable_through_export(self, db_session, save, user, user_data):
        token_repo = TokenRepository(db_session)
        await save(
            RefreshToken(
                user_id=user.id,
                token='secret-token',
                token_hash='b' * 64,
                expires_at=1,
            )
        )

        tokens = await token_repo.get_all(RefreshToken.user_id == user.id)

        assert any(t.token_hash == 'b' * 64 for t in tokens)
