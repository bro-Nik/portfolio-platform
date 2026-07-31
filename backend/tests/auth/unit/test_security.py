from freezegun import freeze_time
import pytest

from app.common.exceptions import AuthenticationError
from app.modules.auth.security import SecurityService


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

    def test_create_token_pair_success(self, service, mock):
        user = mock(id=2, email='test@example.com', role='user', is_verified=False, login='test')

        tokens = service.create_token_pair(user)

        assert isinstance(tokens.access_token, str)
        assert len(tokens.access_token) > 0
        assert isinstance(tokens.refresh_token, str)
        assert len(tokens.refresh_token) > 0
        assert isinstance(tokens.refresh_expires_at, int)

    def test_verify_valid_token(self, service, mock):
        user = mock(id=2, email='test@example.com', role='user', is_verified=False, login='test')
        tokens = service.create_token_pair(user)
        payload = service.verify_token(tokens.access_token)

        assert payload['id'] == '2'
        assert payload['role'] == 'user'
        assert payload['type'] == 'access'

    def test_verify_expired_token(self, service, mock):
        user = mock(id=2, email='test@example.com', role='user', is_verified=False, login='test')

        with freeze_time('2026-01-01 12:00:00'):
            tokens = service.create_token_pair(user)

        with (
            freeze_time('2026-01-02 12:00:00'),
            pytest.raises(AuthenticationError, match='Токен устарел'),
        ):
            service.verify_token(tokens.access_token)

    def test_verify_invalid_token(self, service):
        invalid_token = 'invalid.token.string'

        with pytest.raises(AuthenticationError, match='Некорректный токен'):
            service.verify_token(invalid_token)

    def test_token_types_different(self, service, mock):
        user = mock(id=2, email='test@example.com', role='user', is_verified=False, login='test')
        tokens = service.create_token_pair(user)

        assert tokens.access_token != tokens.refresh_token

        access_payload = service.verify_token(tokens.access_token)
        refresh_payload = service.verify_token(tokens.refresh_token)

        assert access_payload['type'] == 'access'
        assert refresh_payload['type'] == 'refresh'
        assert 'login' in access_payload
        assert 'login' not in refresh_payload

    def test_hash_token(self, service):
        token = 'test.refresh.token'
        h = service.hash_token(token)

        assert isinstance(h, str)
        assert len(h) == 64
        assert service.hash_token(token) == h
        assert service.hash_token('different') != h

    def test_create_and_verify_email_token(self, service):
        user_id = 42
        token = service.create_email_verification_token(user_id)

        assert isinstance(token, str)
        assert len(token) > 0

        decoded_id, new_email = service.verify_email_token(token)
        assert decoded_id == user_id
        assert new_email is None

    def test_create_and_verify_email_token_with_new_email(self, service):
        user_id = 42
        new_email = 'new@example.com'
        token = service.create_email_verification_token(user_id, new_email=new_email)

        decoded_id, decoded_new_email = service.verify_email_token(token)
        assert decoded_id == user_id
        assert decoded_new_email == new_email

    def test_verify_email_token_wrong_type(self, service, mock):
        user = mock(id=2, email='test@example.com', role='user', is_verified=False, login='test')
        access_token = service._create_access_token(user)

        with pytest.raises(AuthenticationError, match='Невалидный токен подтверждения'):
            service.verify_email_token(access_token)

    def test_verify_email_token_expired(self, service):
        with freeze_time('2026-01-01 12:00:00'):
            token = service.create_email_verification_token(1)

        with (
            freeze_time('2027-01-01 12:00:00'),
            pytest.raises(AuthenticationError, match='Токен устарел'),
        ):
            service.verify_email_token(token)

    def test_verify_email_token_invalid(self, service):
        with pytest.raises(AuthenticationError, match='Некорректный токен'):
            service.verify_email_token('not.a.valid.token')
