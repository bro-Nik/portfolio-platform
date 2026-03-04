from datetime import UTC, datetime, timedelta

from freezegun import freeze_time
import pytest
from shared.exceptions import AuthenticationError

from app.core import SecurityService


@pytest.fixture
def service():
    return SecurityService


class TestSecurityService:
    def test_get_password_hash(self, service):
        password = 'test_password'
        hashed = service.get_password_hash(password)

        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_verify_password_correct(self, service):
        password = 'test_password'
        hashed = service.get_password_hash(password)

        assert service.verify_password(password, hashed) is True

    def test_verify_password_incorrect(self, service):
        password = 'test_password'
        hashed = service.get_password_hash(password)
        wrong_password = 'wrong_password'

        assert service.verify_password(wrong_password, hashed) is False

    def test_verify_password_special_characters(self, service):
        special_password = '!@#$%^&*()_+-=[]{}|;:,.<>?/~`'
        hashed = service.get_password_hash(special_password)

        assert service.verify_password(special_password, hashed) is True

    # def test_create_access_token(self, service, mock_user):
    #     token = service.create_access_token(mock_user)
    #
    #     assert isinstance(token, str)
    #     assert len(token) > 0

    # def test_create_refresh_token(self, service, mock_user):
    #     token = service.create_refresh_token(mock_user)
    #
    #     assert isinstance(token, str)
    #     assert len(token) > 0

    # def test_verify_valid_token(self, service, mock_user):
    #     token = service.create_access_token(mock_user)
    #     payload = service.verify_token(token)
    #
    #     assert payload['sub'] == '1'
    #     assert payload['role'] == 'user'
    #     assert payload['type'] == 'access'

    # def test_verify_expired_token(self, service, mock_user):
    #     with freeze_time('2026-01-01 12:00:00'):
    #         token = service.create_access_token(mock_user)
    #
    #     with (
    #         freeze_time('2026-01-02 12:00:00'),
    #         pytest.raises(AuthenticationError, match='Токен устарел'),
    #     ):
    #         service.verify_token(token)

    def test_verify_invalid_token(self, service):
        invalid_token = 'invalid.token.string'

        with pytest.raises(AuthenticationError, match='Некорректный токен'):
            service.verify_token(invalid_token)

    # def test_token_types_different(self, service, mock_user):
    #     access_token = service.create_access_token(mock_user)
    #     refresh_token = service.create_refresh_token(mock_user)
    #
    #     assert access_token != refresh_token
    #
    #     access_payload = service.verify_token(access_token)
    #     refresh_payload = service.verify_token(refresh_token)
    #
    #     assert access_payload['type'] == 'access'
    #     assert refresh_payload['type'] == 'refresh'
    #     assert 'login' in access_payload
    #     assert 'login' not in refresh_payload
