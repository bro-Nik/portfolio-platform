from datetime import UTC, datetime
from unittest.mock import patch

from fastapi import HTTPException
from freezegun import freeze_time
import pytest

from app.modules.auth.repositories import SessionRepository, TokenRepository
from app.modules.auth.services.session import SessionService

user_id = 1


@pytest.fixture
def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = SessionService(db_session, ctx)
    service.token_repo = async_mock(spec=TokenRepository, session=db_session)
    service.repo = async_mock(spec=SessionRepository, session=db_session)
    return service


class TestSessionService:
    async def test_create_success(self, service):
        refresh_token_id = 100
        service.ctx.client_ip = '192.168.1.100'
        service.ctx.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        await service.create(refresh_token_id, user_id)

        service.repo.create.assert_called_once()

        call_args = service.repo.create.call_args
        assert call_args is not None

        session_data = call_args[0][0]
        assert session_data['user_id'] == user_id
        assert session_data['refresh_token_id'] == refresh_token_id
        assert session_data['ip_address'] == service.ctx.client_ip
        assert session_data['user_agent'] == service.ctx.user_agent
        assert session_data['device_type'] == 'desktop'
        assert session_data['browser'] == 'Other'
        assert session_data['os'] == 'Windows'

    @freeze_time('2026-01-01 12:00:00', tz_offset=0)
    async def test_update_success(self, service, mock):
        refresh_token_id = 100
        service.ctx.client_ip = '192.168.1.100'
        db_token = mock(id=50)

        with (
            patch.object(service.repo, 'get_by_token_id', return_value=db_token),
        ):
            await service.update(refresh_token_id)

            service.repo.get_by_token_id.assert_called_once_with(refresh_token_id)
            service.repo.update.assert_called_once()

        update_data = service.repo.update.call_args[0][1]
        assert update_data['ip_address'] == service.ctx.client_ip
        assert update_data['last_activity_at'] == datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

    async def test_update_not_found(self, service):
        with (
            patch.object(service.repo, 'get_by_token_id', return_value=None),
        ):
            await service.update(999)

            service.repo.get_by_token_id.assert_called_once_with(999)
            service.repo.update.assert_not_called()

    async def test_get_user_sessions(self, service):
        sessions = ['session1', 'session2']

        with patch.object(service.repo, 'get_all_by_user_id', return_value=sessions):
            result = await service.get_user_sessions(user_id)

            service.repo.get_all_by_user_id.assert_called_once_with(user_id)
            assert result == sessions

    async def test_delete_session_success(self, service, mock):
        session_id = 10
        db_session = mock(id=session_id, user_id=user_id, refresh_token_id=100)

        with (
            patch.object(service.repo, 'get', return_value=db_session),
            patch.object(service.token_repo, 'delete'),
            patch.object(service.repo, 'delete'),
        ):
            await service.delete_session(session_id, user_id)

            service.repo.get.assert_called_once_with(session_id)
            service.token_repo.delete.assert_called_once_with(100)
            service.repo.delete.assert_called_once_with(session_id)

    async def test_delete_session_not_found(self, service):
        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(HTTPException) as exc,
        ):
            await service.delete_session(999, user_id)

            assert exc.value.status_code == 404

    async def test_delete_session_wrong_user(self, service, mock):
        session_id = 10
        db_session = mock(id=session_id, user_id=999, refresh_token_id=100)

        with (
            patch.object(service.repo, 'get', return_value=db_session),
            pytest.raises(HTTPException) as exc,
        ):
            await service.delete_session(session_id, user_id)

            assert exc.value.status_code == 404
