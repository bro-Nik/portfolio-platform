from unittest.mock import patch

import pytest

from app.common.exceptions import AuthenticationError
from app.common.schemas import AuthUser

from app.modules.auth.repositories import TokenRepository
from app.modules.auth.schemas import RegisterResponse, UserRole
from app.modules.auth.security import SecurityService
from app.modules.auth.services.auth import AuthService, AuthResult, RegisterResult, RegisterTaskData
from app.modules.auth.services.session import SessionService
from app.modules.auth.services.user import UserService
user_id = 1


def _check_created_with_authuser(mock_call, user):
    mock_call.assert_called_once()
    call_auth_user = mock_call.call_args[0][0]
    assert isinstance(call_auth_user, AuthUser)
    assert call_auth_user.id == user.id
    assert call_auth_user.role == UserRole(user.role)


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
        user = mock(id=1, role='user', email='test@example.com', is_verified=False)
        verify_token = 'email.verify.token'
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.user_service, 'create', return_value=user),
            patch.object(service.security, 'create_email_verification_token', return_value=verify_token),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.security, 'hash_token', return_value='token_hash_str'),
            patch.object(service.token_repo, 'create', return_value=db_token),
        ):
            result = await service.register(register_data)

            service.user_service.create.assert_called_once()
            created_user_request = service.user_service.create.call_args[0][0]
            assert created_user_request.email == register_data.email
            assert created_user_request.password == register_data.password
            assert created_user_request.role == UserRole.USER

            service.security.create_email_verification_token.assert_called_once_with(user.id)
            service.security.create_token_pair.assert_called_once()
            service.token_repo.create.assert_called_once()

            assert isinstance(result, RegisterResult)
            assert result.email == user.email
            assert result.verification_token == verify_token
            assert result.tokens.access_token == 'access'
            assert result.tokens.refresh_token == 'refresh'

    async def test_login_success(self, service, mock, data):
        login_data = data(email='test@example.com', password='password123')
        user = mock(id=1, password_hash='hashed', role='user', email='test@example.com', is_verified=True)
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.security, 'verify_password', return_value=True),
            patch.object(service.security, 'hash_token', return_value='token_hash_str'),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.token_repo, 'create', return_value=db_token),
        ):
            result = await service.login(login_data)

            service.user_service.get_for_auth.assert_called_once_with(email=login_data.email)
            service.security.verify_password.assert_called_once_with(login_data.password, user.password_hash)
            _check_created_with_authuser(service.security.create_token_pair, user)
            service.token_repo.create.assert_called_once()
            assert isinstance(result, AuthResult)

    async def test_login_success_unverified(self, service, mock, data):
        login_data = data(email='test@example.com', password='password123')
        user = mock(id=1, password_hash='hashed', role='user', email='test@example.com', is_verified=False)
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.security, 'verify_password', return_value=True),
            patch.object(service.security, 'hash_token', return_value='token_hash_str'),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.token_repo, 'create', return_value=db_token),
        ):
            result = await service.login(login_data)

            service.user_service.get_for_auth.assert_called_once_with(email=login_data.email)
            service.security.verify_password.assert_called_once_with(login_data.password, user.password_hash)
            _check_created_with_authuser(service.security.create_token_pair, user)
            service.token_repo.create.assert_called_once()
            assert isinstance(result, AuthResult)

    async def test_login_wrong_password(self, service, mock, data):
        login_data = data(email='test@example.com', password='password123')
        user = mock(id=1, role='user', email='test@example.com', is_verified=True)

        with (
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.security, 'verify_password', return_value=False),
            pytest.raises(AuthenticationError, match='Неверный email или пароль'),
        ):
            await service.login(login_data)

    async def test_refresh_tokens_success(self, service, mock, data):
        user = mock(id=1, role='user', email='test@example.com', is_verified=False)
        payload = {'id': '1', 'type': 'refresh', 'exp': 9999999999}
        token_data = data(token='valid.refresh.token')
        updated_token = mock(token='new.refresh.token')
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.security, 'hash_token', return_value='hashed_token'),
            patch.object(service.token_repo, 'get_by_token_hash', return_value=db_token),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.token_repo, 'update', return_value=updated_token),
        ):
            result = await service.refresh_tokens(token_data)

            service.security.verify_token.assert_called_once()
            assert service.security.hash_token.call_args_list[0][0][0] == token_data.token
            service.token_repo.get_by_token_hash.assert_called_once_with('hashed_token')
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
            patch.object(service.security, 'hash_token', return_value='hashed_token'),
            patch.object(service.token_repo, 'get_by_token_hash', return_value=None),
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
        user = mock(id=1, role='user', email='test@example.com', is_verified=False)
        token_data = data(token='used.refresh.token')
        payload = {'id': '1', 'type': 'refresh', 'exp': 9999999999}
        updated_token = mock(token='new.refresh.token')
        tokens = mock(access_token='access', refresh_token='refresh')
        db_token = mock(id=99)

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.security, 'hash_token', return_value='hashed_token'),
            patch.object(service.token_repo, 'get_by_token_hash', return_value=db_token),
            patch.object(service.security, 'create_token_pair', return_value=tokens),
            patch.object(service.token_repo, 'update', return_value=updated_token),
        ):
            await service.refresh_tokens(token_data)

            service.token_repo.update.assert_called_once()
            assert service.token_repo.update.call_args[0][1]['token_hash'] == 'hashed_token'

    async def test_logout_success(self, service, mock):
        token = 'valid.token.to.logout'
        db_token = mock(id=99)

        with (
            patch.object(service.security, 'hash_token', return_value='hashed_token'),
            patch.object(service.token_repo, 'get_by_token_hash', return_value=db_token),
            patch.object(service.token_repo, 'delete', return_value=True),
        ):
            result = await service.logout(token)

            service.security.hash_token.assert_called_once_with(token)
            service.token_repo.get_by_token_hash.assert_called_once_with('hashed_token')
            service.token_repo.delete.assert_called_once_with(db_token.id)
            assert result is True

    async def test_logout_all_success(self, service):
        with (
            patch.object(service.token_repo, 'delete_all_by_user', return_value=3),
        ):
            result = await service.logout_all(user_id)

            service.token_repo.delete_all_by_user.assert_called_once_with(user_id)
            assert result is True

    async def test_verify_email_success(self, service, mock, data, async_mock):
        token = 'valid.verify.token'
        user = mock(id=1, is_verified=False)
        repo_mock = async_mock()
        service.user_service.repo = repo_mock

        with (
            patch.object(service.security, 'verify_email_token', return_value=(user.id, None)),
            patch.object(service.user_service, 'get_for_auth', return_value=user),
        ):
            result = await service.verify_email(token)

            service.security.verify_email_token.assert_called_once_with(token)
            service.user_service.get_for_auth.assert_called_once_with(id=user.id)
            repo_mock.update.assert_called_once_with(user.id, {'is_verified': True})
            assert 'подтверждён' in result.message

    async def test_verify_email_already_verified(self, service, mock, data, async_mock):
        token = 'already.verified.token'
        user = mock(id=1, is_verified=True)
        repo_mock = async_mock()
        service.user_service.repo = repo_mock

        with (
            patch.object(service.security, 'verify_email_token', return_value=(user.id, None)),
            patch.object(service.user_service, 'get_for_auth', return_value=user),
        ):
            result = await service.verify_email(token)

            assert 'уже подтверждён' in result.message
            repo_mock.update.assert_not_called()

    async def test_verify_email_with_new_email(self, service, mock, data, async_mock):
        token = 'email.change.token'
        new_email = 'new@example.com'
        user = mock(id=1, email='old@example.com', is_verified=False)
        repo_mock = async_mock()
        service.user_service.repo = repo_mock

        with (
            patch.object(service.security, 'verify_email_token', return_value=(user.id, new_email)),
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.user_service.repo, 'exists_by', return_value=False),
        ):
            result = await service.verify_email(token)

            repo_mock.update.assert_called_once_with(user.id, {'email': new_email, 'is_verified': True})
            assert 'подтверждён' in result.message

    async def test_resend_verification_success(self, service, mock, data):
        email = 'test@example.com'
        user = mock(id=1, email=email, is_verified=False)
        verify_token = 'new.verify.token'

        with (
            patch.object(service.user_service, 'get_for_auth', return_value=user),
            patch.object(service.security, 'create_email_verification_token', return_value=verify_token),
        ):
            result = await service.resend_verification(email)

            service.user_service.get_for_auth.assert_called_once_with(email=email)
            service.security.create_email_verification_token.assert_called_once_with(user.id)

            assert isinstance(result, RegisterTaskData)
            assert result.email == user.email
            assert result.token == verify_token
            assert 'отправлено повторно' in result.message

    async def test_resend_verification_already_verified(self, service, mock, data):
        email = 'test@example.com'
        user = mock(id=1, email=email, is_verified=True)

        with (
            patch.object(service.user_service, 'get_for_auth', return_value=user),
        ):
            result = await service.resend_verification(email)

            assert isinstance(result, RegisterResponse)
            assert 'уже подтверждён' in result.message
