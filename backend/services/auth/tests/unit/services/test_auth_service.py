from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from freezegun import freeze_time
import pytest
from shared.exceptions import AuthenticationError

from app.schemas import AuthUser, TokensResponse, UserRole
from app.services import AuthService
from app.services.auth import AuthResult


@pytest.fixture
def service(mock_async_session, mock_token_repo, mock_user_service, mock_security_service):
    return AuthService(
        session=mock_async_session,
        token_repo=mock_token_repo,
        user_service=mock_user_service,
        security=mock_security_service,
    )


class TestAuthService:
    async def test_register_success(self, service, mock_login_data, mock_db_user, mock_token_pair, mock_db_token):
        with (
            patch.object(service.user_service, 'create', return_value=mock_db_user),
            patch.object(service.security, 'create_token_pair', return_value=mock_token_pair),
            patch.object(service.token_repo, 'create', return_value=mock_db_token),
        ):
            result = await service.register(mock_login_data)

            service.user_service.create.assert_called_once()
            created_user_request = service.user_service.create.call_args[0][0]
            assert created_user_request.email == mock_login_data.email
            assert created_user_request.password == mock_login_data.password
            assert created_user_request.role == UserRole.USER

            service.security.create_token_pair.assert_called_once()
            service.token_repo.create.assert_called_once()

            assert isinstance(result, AuthResult)
            assert result.user_id == mock_db_user.id
            assert result.refresh_token_id == mock_db_token.id
            assert result.tokens.access_token == mock_token_pair.access_token
            assert result.tokens.refresh_token == mock_token_pair.refresh_token

    async def test_login_success(self, service, mock_login_data, mock_db_user, mock_token_pair, mock_db_token):
        with (
            patch.object(service.user_service, 'get_by_email', return_value=mock_db_user),
            patch.object(service.security, 'verify_password', return_value=True),
            patch.object(service.security, 'create_token_pair', return_value=mock_token_pair),
            patch.object(service.token_repo, 'create', return_value=mock_db_token),
        ):
            result = await service.login(mock_login_data)

            service.user_service.get_by_email.assert_called_once_with('test@example.com')
            service.security.verify_password.assert_called_once()
            service.security.create_token_pair.assert_called_once()
            service.token_repo.create.assert_called_once()
            assert isinstance(result, AuthResult)

    async def test_login_wrong_password(self, service, mock_login_data, mock_db_user):
        with (
            patch.object(service.user_service, 'get_by_email', return_value=mock_db_user),
            patch.object(service.security, 'verify_password', return_value=False),
            pytest.raises(AuthenticationError, match='Неверный email или пароль'),
        ):
            await service.login(mock_login_data)

    async def test_refresh_tokens_success(self, service, mock_db_user, mock_db_token, mock_token_pair):
        token_data = MagicMock()
        token_data.token = 'valid.refresh.token'
        payload = {'sub': '1', 'type': 'refresh', 'exp': 9999999999}
        updated_token = MagicMock()
        updated_token.token = 'new.refresh.token'

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            patch.object(service.security, 'create_token_pair', return_value=mock_token_pair),
            patch.object(service.user_service, 'get', return_value=mock_db_user),
            patch.object(service.token_repo, 'update', return_value=updated_token),
        ):
            result = await service.refresh_tokens(token_data)

            service.security.verify_token.assert_called_once()
            service.token_repo.get_by_token.assert_called_once_with(token_data.token)
            service.security.create_token_pair.assert_called_once()
            service.token_repo.update.assert_called_once()
            assert isinstance(result, AuthResult)

    async def test_refresh_tokens_invalid_type(self, service):
        token_data = MagicMock()
        token_data.token = 'access.token.not.refresh'
        payload = {'sub': '1', 'type': 'access', 'exp': 9999999999}

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            pytest.raises(AuthenticationError, match='Невалидный refresh токен'),
        ):
            await service.refresh_tokens(token_data)

    async def test_refresh_tokens_not_found_in_db(self, service):
        token_data = MagicMock()
        token_data.token = 'valid.but.not.in.db'
        payload = {'sub': '1', 'type': 'refresh', 'exp': 9999999999}

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.token_repo, 'get_by_token', return_value=None),
            pytest.raises(AuthenticationError, match='Токен не найден'),
        ):
            await service.refresh_tokens(token_data)

    async def test_refresh_tokens_expired(self, service):
        token_data = MagicMock()
        token_data.token = 'expired.token'

        with (
            patch.object(service.security, 'verify_token', side_effect=AuthenticationError('Token expired')),
            pytest.raises(AuthenticationError, match='Token expired'),
        ):
            await service.refresh_tokens(token_data)

    async def test_token_replaced_after_refresh(self, service, mock_db_user, mock_db_token, mock_token_pair):
        token_data = MagicMock()
        token_data.token = 'used.refresh.token'
        payload = {'sub': '1', 'type': 'refresh', 'exp': 9999999999}
        updated_token = MagicMock()
        updated_token.token = 'new.refresh.token'

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.user_service, 'get', return_value=mock_db_user),
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            patch.object(service.security, 'create_token_pair', return_value=mock_token_pair),
            patch.object(service.token_repo, 'update', return_value=updated_token),
        ):
            await service.refresh_tokens(token_data)

            service.token_repo.update.assert_called_once()
            assert service.token_repo.update.call_args[0][1].token == mock_token_pair.refresh_token

    async def test_logout_success(self, service, mock_db_token):
        token = 'valid.token.to.logout'

        with (
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            patch.object(service.token_repo, 'delete', return_value=True),
        ):
            result = await service.logout(token)

            service.token_repo.get_by_token.assert_called_once_with(token)
            service.token_repo.delete.assert_called_once_with(100)

        assert result is True

    async def test_logout_all_success(self, service):
        user_id = 1
        with (
            patch.object(service.token_repo, 'delete_many_by_user', return_value=3),  # Удалено 3 токена
        ):
            result = await service.logout_all(user_id)

            # Проверяем что токены удаляются
            service.token_repo.delete_many_by_user.assert_called_once_with(user_id)

        assert result is True
