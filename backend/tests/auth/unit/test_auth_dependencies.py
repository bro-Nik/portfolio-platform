from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.common.dependencies.auth import get_actor_from_headers, get_current_user
from app.common.exceptions import UnauthorizedException
from app.common.schemas import UserRole
from app.core import settings

ALGORITHM = settings.jwt_algorithm


def _encode(payload: dict) -> str:
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def _bearer(token: str) -> str:
    return f'Bearer {token}'


class _Credentials:
    def __init__(self, token: str) -> None:
        self.credentials = token
        self.scheme = 'Bearer'


def _access_token(user_id: int = 1, role: UserRole = UserRole.USER) -> str:
    return _encode(
        {
            'id': str(user_id),
            'role': role.value,
            'type': 'access',
            'exp': int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        }
    )


def _refresh_token(user_id: int = 1) -> str:
    return _encode(
        {
            'id': str(user_id),
            'type': 'refresh',
            'exp': int((datetime.now(UTC) + timedelta(days=1)).timestamp()),
        }
    )


def _password_reset_token(user_id: int = 1) -> str:
    return _encode(
        {
            'id': str(user_id),
            'type': 'password_reset',
            'exp': int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        }
    )


def _email_verify_token(user_id: int = 1) -> str:
    return _encode(
        {
            'id': str(user_id),
            'type': 'email_verify',
            'exp': int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
        }
    )


NON_ACCESS_TOKENS = {
    'refresh': _refresh_token,
    'password_reset': _password_reset_token,
    'email_verify': _email_verify_token,
}


class TestGetCurrentUserTokenType:
    def test_accepts_access_token(self):
        user = get_current_user(_Credentials(_access_token(7, UserRole.ADMIN)))

        assert user.id == 7
        assert user.role == UserRole.ADMIN

    @pytest.mark.parametrize('factory', NON_ACCESS_TOKENS.values(), ids=list(NON_ACCESS_TOKENS))
    def test_rejects_non_access_token(self, factory):
        # Refresh / reset / verify tokens carry no role claim, so without a type
        # check AuthUser would silently default them to a regular user identity.
        with pytest.raises(UnauthorizedException):
            get_current_user(_Credentials(factory()))

    def test_rejects_token_without_type(self):
        token = _encode(
            {
                'id': '7',
                'role': 'user',
                'exp': int((datetime.now(UTC) + timedelta(hours=1)).timestamp()),
            }
        )

        with pytest.raises(UnauthorizedException):
            get_current_user(_Credentials(token))

    def test_rejects_expired_access_token(self):
        token = _encode(
            {
                'id': '7',
                'role': 'user',
                'type': 'access',
                'exp': int((datetime.now(UTC) - timedelta(hours=1)).timestamp()),
            }
        )

        with pytest.raises(UnauthorizedException, match='Токен устарел'):
            get_current_user(_Credentials(token))


class TestGetActorFromHeaders:
    def test_returns_user_for_access_token(self):
        user = get_actor_from_headers(_bearer(_access_token(3)))

        assert user is not None
        assert user.id == 3

    @pytest.mark.parametrize('factory', NON_ACCESS_TOKENS.values(), ids=list(NON_ACCESS_TOKENS))
    def test_returns_none_for_non_access_token(self, factory):
        assert get_actor_from_headers(_bearer(factory())) is None

    def test_returns_none_for_missing_or_malformed_header(self):
        assert get_actor_from_headers(None) is None
        assert get_actor_from_headers('Basic abc') is None
        assert get_actor_from_headers('Bearer') is None
        assert get_actor_from_headers('Bearer not.a.jwt') is None
