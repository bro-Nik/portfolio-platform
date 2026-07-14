from unittest.mock import patch

import pytest

from app.common.exceptions import AuthenticationError
from app.common.schemas import AuthUser

from app.modules.auth.repositories import TokenRepository
from app.modules.auth.schemas import UserRole
from app.modules.auth.security import SecurityService
from app.modules.auth.services.auth import AuthService, AuthResult
from app.modules.auth.services.session import SessionService
from app.modules.auth.services.user import UserService
user_id = 1


def _check_created_with_authuser(mock_call, user):
    mock_call.assert_called_once()
    call_auth_user = mock_call.call_args[0][0]
    assert isinstance(call_auth_user, AuthUser)
    assert call_auth_user.id == user.id
    assert call_auth_user.role == UserRole(user.role)
    assert call_auth_user.email == user.email


@pytest.fixture
def service(db_session, async_mock, mock, data):
    ctx = data(actor=data(id=user_id))
    service = AuthService(db_session, ctx)
    service.token_repo = async_mock(spec=TokenRepository, session=db_session)
    service.user_service = async_mock(spec=UserService, session=db_session, ctx=ctx)
    service.session_service = async_mock(spec=SessionService, session=db_session, ctx=ctx)
    service.security = mock(spec=SecurityService)
    return service


class TestAuthService:
    async def test_register_success(self, service, mock, data):
        register_data = data(email='test@example.com', password='password123')
        user = mock(id=1, role='user', email='test@example.com')
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.user_service, 'create', return_value=user),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.token_repo, 'create', return_value=db_token),
        ):
            result = await service.register(register_data)

            service.user_service.create.assert_called_once()
            created_user_request = service.user_service.create.call_args[0][0]
            assert created_user_request.email == register_data.email
            assert created_user_request.password == register_data.password
            assert created_user_request.role == UserRole.USER

            _check_created_with_authuser(service.security.create_token_pair, user)
            service.token_repo.create.assert_called_once()

            assert isinstance(result, AuthResult)
            assert result.user_id == user.id
            assert result.refresh_token_id == db_token.id
            assert result.tokens.access_token == tokens.access_token
            assert result.tokens.refresh_token == tokens.refresh_token

    async def test_login_success(self, service, mock, data):
        login_data = data(email='test@example.com', password='password123')
        user = mock(id=1, password_hash='hashed', role='user', email='test@example.com')
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.security, 'verify_password', return_value=True),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.token_repo, 'create', return_value=db_token),
        ):
            result = await service.login(login_data)

            service.user_service.get_for_auth.assert_called_once_with(email=login_data.email)
            service.security.verify_password.assert_called_once_with(login_data.password, user.password_hash)
            service.security.verify_password.assert_called_once()
            _check_created_with_authuser(service.security.create_token_pair, user)
            service.token_repo.create.assert_called_once()
            assert isinstance(result, AuthResult)

    async def test_login_wrong_password(self, service, mock, data):
        login_data = data(email='test@example.com', password='password123')
        user = mock(id=1, role='user', email='test@example.com')

        with (
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.security, 'verify_password', return_value=False),
            pytest.raises(AuthenticationError, match='Неверный email или пароль'),
        ):
            await service.login(login_data)

    async def test_refresh_tokens_success(self, service, mock, data):
        user = mock(id=1, role='user', email='test@example.com')
        payload = {'id': '1', 'type': 'refresh', 'exp': 9999999999}
        token_data = data(token='valid.refresh.token')
        updated_token = mock(token='new.refresh.token')
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.token_repo, 'get_by_token', return_value=db_token),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.token_repo, 'update', return_value=updated_token),
        ):
            result = await service.refresh_tokens(token_data)

            service.security.verify_token.assert_called_once()
            service.token_repo.get_by_token.assert_called_once_with(token_data.token)
            _check_created_with_authuser(service.security.create_token_pair, user)
            service.token_repo.update.assert_called_once()
            assert isinstance(result, AuthResult)

    async def test_refresh_tokens_invalid_type(self, service, data):
        token_data = data(token='access.token.not.refresh')
        payload = {'id': '1', 'type': 'access', 'exp': 9999999999}

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            pytest.raises(AuthenticationError, match='Невалидный refresh токен'),
        ):
            await service.refresh_tokens(token_data)

    async def test_refresh_tokens_not_found_in_db(self, service, data):
        token_data = data(token='valid.but.not.in.db')
        payload = {'id': '1', 'type': 'refresh', 'exp': 9999999999}

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.token_repo, 'get_by_token', return_value=None),
            pytest.raises(AuthenticationError, match='Токен не найден'),
        ):
            await service.refresh_tokens(token_data)

    async def test_refresh_tokens_expired(self, service, data):
        token_data = data(token='expired.token')

        with (
            patch.object(service.security, 'verify_token', side_effect=AuthenticationError('Token expired')),
            pytest.raises(AuthenticationError, match='Token expired'),
        ):
            await service.refresh_tokens(token_data)

    async def test_token_replaced_after_refresh(self, service, mock, data):
        user = mock(id=1, role='user', email='test@example.com')
        token_data = data(token='used.refresh.token')
        payload = {'id': '1', 'type': 'refresh', 'exp': 9999999999}
        updated_token = mock(token='new.refresh.token')
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.token_repo, 'get_by_token', return_value=db_token),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.token_repo, 'update', return_value=updated_token),
        ):
            await service.refresh_tokens(token_data)

            service.token_repo.update.assert_called_once()
            assert service.token_repo.update.call_args[0][1]['token'] == tokens.refresh_token

    async def test_logout_success(self, service, mock):
        token = 'valid.token.to.logout'
        db_token = mock(id=99)

        with (
            patch.object(service.token_repo, 'get_by_token', return_value=db_token),
            patch.object(service.token_repo, 'delete', return_value=True),
        ):
            result = await service.logout(token)

            service.token_repo.get_by_token.assert_called_once_with(token)
            service.token_repo.delete.assert_called_once_with(db_token.id)
            assert result is True

    async def test_logout_all_success(self, service):
        with (
            patch.object(service.token_repo, 'delete_all_by_user', return_value=3),
        ):
            result = await service.logout_all(user_id)

            service.token_repo.delete_all_by_user.assert_called_once_with(user_id)
            assert result is True
