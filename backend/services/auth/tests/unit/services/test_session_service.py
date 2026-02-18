from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

from freezegun import freeze_time
import pytest

from app.schemas import LoginSessionCreate, LoginSessionUpdate
from app.services.session import SessionService


class TestSessionService:
    """Тесты SessionService."""

    @pytest.fixture
    def service(self, mock_async_session, mock_session_repo, mock_token_repo):
        """Фикстура для создания SessionService."""
        return SessionService(
            session=mock_async_session,
            session_repo=mock_session_repo,
            token_repo=mock_token_repo,
        )

    @pytest.mark.asyncio
    async def test_create_session_success(self, service, mock_request):
        """Тест успешного создания сессии."""
        user_id = 1
        refresh_token_id = 100
        ip = '192.168.1.100'

        with (
            patch('app.services.session.get_real_ip', return_value=ip),
        ):
            await service.create_session(user_id, refresh_token_id, mock_request)

        service.repo.create.assert_called_once()

        # Проверяем аргументы вызова
        call_args = service.repo.create.call_args
        assert call_args is not None

        session_data = call_args[0][0]
        assert isinstance(session_data, LoginSessionCreate)
        assert session_data.user_id == user_id
        assert session_data.refresh_token_id == refresh_token_id
        assert session_data.ip_address == ip
        assert session_data.user_agent == mock_request.headers['user-agent']
        assert session_data.device_type == 'desktop'
        assert session_data.browser == 'Other'
        assert session_data.os == 'Windows'

    @pytest.mark.asyncio
    async def test_create_session_no_headers(self, service, mock_request):
        """Тест создания сессии без заголовков."""
        user_id = 1
        refresh_token_id = 100

        # Пустые заголовки
        mock_request.headers = {}

        with (
            patch('app.services.session.get_real_ip', return_value=None),
        ):
            await service.create_session(user_id, refresh_token_id, mock_request)

        service.repo.create.assert_called_once()

        session_data = service.repo.create.call_args[0][0]
        assert session_data.ip_address is None
        assert session_data.user_agent is None
        assert session_data.device_type is None
        assert session_data.browser is None
        assert session_data.os is None

    @pytest.mark.asyncio
    @freeze_time('2026-01-01 12:00:00', tz_offset=0)
    async def test_update_session_success(self, service, mock_request):
        """Тест успешного обновления сессии."""
        refresh_token_id = 100
        ip = '10.0.0.1'

        with (
            patch.object(service.repo, 'get_by_token_id', return_value=MagicMock(id=50)),
            patch('app.services.session.get_real_ip', return_value=ip),
        ):
            await service.update_session(refresh_token_id, mock_request)

            service.repo.get_by_token_id.assert_called_once_with(refresh_token_id)
            service.repo.update.assert_called_once()

        update_data = service.repo.update.call_args[0][1]
        assert isinstance(update_data, LoginSessionUpdate)
        assert update_data.ip_address == ip
        assert update_data.last_activity_at == datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

    @pytest.mark.asyncio
    async def test_update_session_not_found(self, service, mock_request):
        """Тест обновления несуществующей сессии."""
        refresh_token_id = 999

        with (
            patch.object(service.repo, 'get_by_token_id', return_value=None),
        ):
            await service.update_session(refresh_token_id, mock_request)

            service.repo.get_by_token_id.assert_called_once_with(refresh_token_id)
            service.repo.update.assert_not_called()
