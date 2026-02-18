from datetime import UTC, datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from app.core.exceptions import AuthenticationError
from app.schemas import TokensResponse, UserRole
from app.services.auth import AuthService


class TestAuthService:
    """Тесты для AuthService."""

    @pytest.fixture
    def service(self, mock_async_session, mock_token_repo, mock_user_service, mock_security_service):
        """Фикстура для создания AuthService с контролируемыми зависимостями."""
        return AuthService(
            session=mock_async_session,
            token_repo=mock_token_repo,
            user_service=mock_user_service,
            security=mock_security_service,
        )

    @pytest.mark.asyncio
    async def test_register_success(self, service, mock_login_data, mock_db_user):
        """Тест успешной регистрации."""
        mock_tokens = TokensResponse(access_token='access', refresh_token='refresh', token_type='bearer')

        with (
            patch.object(service.user_service, 'create_user', return_value=mock_db_user),
            patch.object(service, '_create_tokens', return_value=(mock_tokens, 1, 100)),
        ):
            tokens, user_id, token_id = await service.register(mock_login_data)

            service.user_service.create_user.assert_called_once()
            assert user_id == 1
            assert token_id == 100
            assert tokens == mock_tokens

    @pytest.mark.asyncio
    async def test_register_user_service_error(self, service, mock_login_data):
        """Тест регистрации при ошибке в user_service."""
        with (
            patch.object(service.user_service, 'create_user', side_effect=ValueError('UserLogin')),
            pytest.raises(ValueError, match='UserLogin'),
        ):
            await service.register(mock_login_data)


    @pytest.mark.asyncio
    async def test_login_success(self, service, mock_login_data, mock_db_user):
        """Тест успешного входа."""
        mock_tokens = TokensResponse(access_token='access', refresh_token='refresh', token_type='bearer')

        with (
            patch.object(service.user_service, 'get_user_by_email', return_value=mock_db_user),
            patch.object(service.security, 'verify_password', return_value=True),
            patch.object(service, '_create_tokens', return_value=(mock_tokens, 1, 100)),
        ):
            tokens, user_id, token_id = await service.login(mock_login_data)

            service.user_service.get_user_by_email.assert_called_once_with('test@example.com')
            service.security.verify_password.assert_called_once()
            assert user_id == 1
            assert token_id == 100
            assert tokens == mock_tokens

    @pytest.mark.asyncio
    async def test_login_user_not_found(self, service, mock_login_data):
        """Тест входа с несуществующим пользователем."""
        with (
            patch.object(service.user_service, 'get_user_by_email', return_value=None),
            pytest.raises(AuthenticationError, match='Неверный email или пароль'),
        ):
            await service.login(mock_login_data)

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, service, mock_login_data, mock_db_user):
        """Тест входа с неверным паролем."""
        with (
            patch.object(service.user_service, 'get_user_by_email', return_value=mock_db_user),
            patch.object(service.security, 'verify_password', return_value=False),
            pytest.raises(AuthenticationError, match='Неверный email или пароль'),
        ):
            await service.login(mock_login_data)

    @pytest.mark.asyncio
    async def test_refresh_tokens_success(self, service, mock_db_user, mock_db_token):
        """Тест успешного обновления токенов."""
        token = 'valid.refresh.token'
        payload = {'sub': '1', 'type': 'refresh', 'exp': 9999999999}

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            patch.object(service.security, 'is_token_expired', return_value=False),
            patch.object(service.user_service, 'get_user_by_id', return_value=mock_db_user),
            patch.object(service, '_generate_tokens', return_value=('new_access', 'new_refresh', 9999999999)),
        ):
            tokens, user_id, token_id = await service.refresh_tokens(token)

            service.security.verify_token.assert_called_once_with(token)
            service.token_repo.get_by_token.assert_called_once_with(token)
            service.token_repo.update.assert_called_once()
            assert user_id == 1
            assert token_id == 100
            assert tokens.access_token == 'new_access'
            assert tokens.refresh_token == 'new_refresh'

    @pytest.mark.asyncio
    async def test_refresh_tokens_invalid_type(self, service):
        """Тест обновления с токеном неверного типа."""
        access_token = 'access.token.not.refresh'
        payload = {'sub': '1', 'type': 'access', 'exp': 9999999999}

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            pytest.raises(AuthenticationError, match='Невалидный refresh токен'),
        ):
            await service.refresh_tokens(access_token)

    @pytest.mark.asyncio
    async def test_refresh_tokens_not_found_in_db(self, service):
        """Тест обновления с токеном, которого нет в БД."""
        token = 'valid.but.not.in.db'
        payload = {'sub': '1', 'type': 'refresh', 'exp': 9999999999}

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.token_repo, 'get_by_token', return_value=None),
            pytest.raises(AuthenticationError, match='Токен не найден'),
        ):
            await service.refresh_tokens(token)

    @pytest.mark.asyncio
    async def test_refresh_tokens_expired(self, service, mock_db_token):
        """Тест обновления истекшего токена."""
        token = 'expired.token'
        payload = {'sub': '1', 'type': 'refresh', 'exp': 9999999999}

        mock_db_token.expires_at = 1000000000  # Истекший срок

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.security, 'is_token_expired', return_value=True),
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            pytest.raises(AuthenticationError, match='Токен истек'),
        ):
            await service.refresh_tokens(token)

        service.token_repo.delete.assert_called_once_with(100)

    @freeze_time('2026-01-01 12:00:00')
    @pytest.mark.asyncio
    async def test_refresh_token_near_expiry(self, service, mock_db_user, mock_db_token):
        """Тест обновления токена с истекающим сроком."""
        token = 'almost.expired.token'
        exp_time = int(datetime.now(UTC).timestamp()) + 5  # Токен истекает через 5 секунд
        payload = {'sub': '1', 'type': 'refresh', 'exp': exp_time}
        mock_db_token.expires_at = exp_time

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.security, 'is_token_expired', return_value=False),
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            patch.object(service.user_service, 'get_user_by_id', return_value=mock_db_user),
            patch.object(service, '_generate_tokens', return_value=('access_token', 'refresh_token', 9999999999)),
        ):
            # Должен работать нормально
            await service.refresh_tokens(token)

    @pytest.mark.asyncio
    async def test_prevent_token_reuse(self, service, mock_db_user, mock_db_token):
        """Тест предотвращения повторного использования refresh токена."""
        token = 'used.refresh.token'
        payload = {'sub': '1', 'type': 'refresh', 'exp': 9999999999}

        # Первый успешный вызов
        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.security, 'is_token_expired', return_value=False),
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            patch.object(service.user_service, 'get_user_by_id', return_value=mock_db_user),
            patch.object(service, '_generate_tokens', return_value=('access_token', 'refresh_token', 9999999999)),
        ):
            await service.refresh_tokens(token)

        # Второй вызов с тем же токеном должен падать
        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.token_repo, 'get_by_token', return_value=None),
            pytest.raises(AuthenticationError, match='Токен не найден'),
        ):
            await service.refresh_tokens(token)

    @pytest.mark.asyncio
    async def test_logout_success(self, service, mock_db_token):
        """Тест успешного выхода."""
        token = 'valid.token.to.logout'

        with (
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            patch.object(service.token_repo, 'delete', return_value=True),
        ):
            result = await service.logout(token)

            service.token_repo.get_by_token.assert_called_once_with(token)
            service.token_repo.delete.assert_called_once_with(100)

        assert result is True

    @pytest.mark.asyncio
    async def test_logout_token_not_found(self, service):
        """Тест выхода с несуществующим токеном."""
        token = 'nonexistent.token'

        with (
            patch.object(service.token_repo, 'get_by_token', return_value=None),
        ):
            result = await service.logout(token)

            # Проверяем что токен не удаляется
            service.token_repo.delete.assert_not_called()

        assert result is False

    @pytest.mark.asyncio
    async def test_logout_all_success(self, service):
        """Тест успешного выхода со всех устройств."""
        user_id = 1
        with (
            patch.object(service.token_repo, 'delete_user_tokens', return_value=3),  # Удалено 3 токена
        ):
            result = await service.logout_all(user_id)

            # Проверяем что токены удаляются
            service.token_repo.delete_user_tokens.assert_called_once_with(user_id)

        assert result is True

    @pytest.mark.asyncio
    async def test_logout_all_no_tokens(self, service):
        """Тест выхода со всех устройств когда нет токенов."""
        user_id = 1
        with (
            patch.object(service.token_repo, 'delete_user_tokens', return_value=0),  # Нечего удалять
        ):
            result = await service.logout_all(user_id)

        assert result is False

    @pytest.mark.asyncio
    async def test_create_tokens_success(self, service, mock_db_user, mock_db_token):
        """Тест создания пары токенов."""
        with (
            patch.object(service, '_generate_tokens', return_value=('access_token', 'refresh_token', 9999999999)),
            patch.object(service.token_repo, 'create', return_value=mock_db_token),
        ):
            tokens, user_id, token_id = await service._create_tokens(mock_db_user)

        assert tokens.access_token == 'access_token'
        assert tokens.refresh_token == 'refresh_token'
        assert user_id == 1
        assert token_id == 100

    def test_generate_tokens_success(self, service, mock_db_user):
        """Тест генерации токенов."""
        with (
            patch.object(service.security, 'create_access_token', return_value='access_token'),
            patch.object(service.security, 'create_refresh_token', return_value='refresh_token'),
            patch.object(service.security, 'verify_token', return_value={'exp': 9999999999}),
        ):
            result = service._generate_tokens(mock_db_user)

        assert result == ('access_token', 'refresh_token', 9999999999)

    def test_generate_tokens_user_none(self, service):
        """Тест генерации токенов для None пользователя."""
        with pytest.raises(AuthenticationError, match='Пользователь не найден'):
            service._generate_tokens(None)

    @pytest.mark.asyncio
    async def test_register_preserves_user_data(self, service, mock_db_user, mock_login_data):
        """Тест что регистрация сохраняет все данные пользователя."""
        mock_tokens = TokensResponse(access_token='access', refresh_token='refresh', token_type='bearer')

        with (
            patch.object(service.user_service, 'create_user', return_value=mock_db_user),
            patch.object(service, '_create_tokens', return_value=(mock_tokens, 1, 100)),
        ):
            await service.register(mock_login_data)
            call_args = service.user_service.create_user.call_args

        assert call_args is not None

        # Проверяем что передается UserCreateRequest с ролью USER
        user_create_request = call_args[0][0]
        assert user_create_request.email == 'test@example.com'
        assert user_create_request.role == UserRole.USER

    @pytest.mark.asyncio
    async def test_token_payload_validation_on_refresh(self, service, mock_db_token):
        """Тест валидации payload при обновлении токенов."""
        token = 'valid.token'
        payload = {'type': 'refresh', 'exp': 9999999999}  # без sub

        with (
            patch.object(service.security, 'verify_token', return_value=payload),
            patch.object(service.security, 'is_token_expired', return_value=False),
            patch.object(service.token_repo, 'get_by_token', return_value=mock_db_token),
            pytest.raises(AuthenticationError, match='Невалидный refresh токен'),
        ):
            await service.refresh_tokens(token)
