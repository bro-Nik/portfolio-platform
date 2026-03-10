from datetime import UTC, datetime
from unittest.mock import patch

from freezegun import freeze_time
import pytest

from app.repositories import SessionRepository, TokenRepository
from app.schemas import LoginSessionCreate, LoginSessionUpdate
from app.services import SessionService

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
        assert isinstance(session_data, LoginSessionCreate)
        assert session_data.user_id == user_id
        assert session_data.refresh_token_id == refresh_token_id
        assert session_data.ip_address == service.ctx.client_ip
        assert session_data.user_agent == service.ctx.user_agent
        assert session_data.device_type == 'desktop'
        assert session_data.browser == 'Other'
        assert session_data.os == 'Windows'

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
        assert isinstance(update_data, LoginSessionUpdate)
        assert update_data.ip_address == service.ctx.client_ip
        assert update_data.last_activity_at == datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)

    async def test_update_not_found(self, service):
        with (
            patch.object(service.repo, 'get_by_token_id', return_value=None),
        ):
            await service.update(999)

            service.repo.get_by_token_id.assert_called_once_with(999)
            service.repo.update.assert_not_called()
