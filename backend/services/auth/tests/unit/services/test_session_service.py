from datetime import UTC, datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from app.repositories import SessionRepository, TokenRepository
from app.schemas import LoginSessionCreate, LoginSessionUpdate
from app.services import SessionService


@pytest.fixture
def service(db_session, async_mock):
    return SessionService(
        session=db_session,
        session_repo=async_mock(spec=SessionRepository, session=db_session),
        token_repo=async_mock(spec=TokenRepository, session=db_session),
    )


class TestSessionService:
    async def test_create_session_success(self, service, mock):
        user_id = 1
        refresh_token_id = 100
        ip = '192.168.1.100'
        request = mock(headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

        with (
            patch('app.services.session.get_client_ip', return_value=ip),
        ):
            await service.create(user_id, refresh_token_id, request)

        service.repo.create.assert_called_once()

        call_args = service.repo.create.call_args
        assert call_args is not None

        session_data = call_args[0][0]
        assert isinstance(session_data, LoginSessionCreate)
        assert session_data.user_id == user_id
        assert session_data.refresh_token_id == refresh_token_id
        assert session_data.ip_address == ip
        assert session_data.user_agent == request.headers['user-agent']
        assert session_data.device_type == 'desktop'
        assert session_data.browser == 'Other'
        assert session_data.os == 'Windows'

    async def test_create_session_no_headers(self, service, mock):
        request = mock(headers={})

        with (
            patch('app.services.session.get_client_ip', return_value=None),
        ):
            await service.create(1, 100, request)

        service.repo.create.assert_called_once()

        session_data = service.repo.create.call_args[0][0]
        assert session_data.ip_address is None
        assert session_data.user_agent is None
        assert session_data.device_type is None
        assert session_data.browser is None
        assert session_data.os is None

    @freeze_time('2026-01-01 12:00:00', tz_offset=0)
    async def test_update_session_success(self, service, mock):
        request = mock(headers = {'user-agent': 'Mozilla/5.0'})
        refresh_token_id = 100
        ip = '10.0.0.1'
        db_token = mock(id=50)

        with (
            patch.object(service.repo, 'get_by_token_id', return_value=db_token),
            patch('app.services.session.get_client_ip', return_value=ip),
        ):
            await service.update(refresh_token_id, request)

            service.repo.get_by_token_id.assert_called_once_with(refresh_token_id)
            service.repo.update.assert_called_once()

        update_data = service.repo.update.call_args[0][1]
        assert isinstance(update_data, LoginSessionUpdate)
        assert update_data.ip_address == ip
        assert update_data.last_activity_at == datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

    async def test_update_session_not_found(self, service, mock):
        request = mock(headers = {'user-agent': 'Mozilla/5.0'})
        refresh_token_id = 999

        with (
            patch.object(service.repo, 'get_by_token_id', return_value=None),
        ):
            await service.update(refresh_token_id, request)

            service.repo.get_by_token_id.assert_called_once_with(refresh_token_id)
            service.repo.update.assert_not_called()
