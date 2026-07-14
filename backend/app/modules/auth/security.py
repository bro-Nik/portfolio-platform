from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from app.common.exceptions import AuthenticationError
from app.common.schemas import AuthUser

from app.core import settings


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    refresh_expires_at: int


class SecurityService:
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def create_token_pair(cls, user: AuthUser) -> TokenPair:
        return TokenPair(
            access_token=cls._create_access_token(user),
            refresh_token=cls._create_refresh_token(user),
            refresh_expires_at=cls._get_refresh_token_expiry(),
        )

    @staticmethod
    def verify_token(token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except jwt.ExpiredSignatureError as e:
            raise AuthenticationError('Токен устарел') from e
        except (jwt.InvalidTokenError, ValidationError) as e:
            raise AuthenticationError('Некорректный токен') from e
        except jwt.PyJWTError as e:
            raise AuthenticationError('Ошибка верификации токена') from e

    @classmethod
    def _create_access_token(cls, user: AuthUser) -> str:
        return cls._jwt_encode({
            'id': str(user.id),
            'login': user.email.split('@')[0] if user.email else '',
            'role': user.role.value if hasattr(user.role, 'value') else user.role,
            'type': 'access',
            'exp': cls._get_access_token_expiry(),
        })

    @classmethod
    def _create_refresh_token(cls, user: AuthUser) -> str:
        return cls._jwt_encode({
            'id': str(user.id),
            'type': 'refresh',
            'exp': cls._get_refresh_token_expiry(),
        })

    @classmethod
    def _jwt_encode(cls, payload: dict[str, Any]) -> str:
        return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

    @classmethod
    def _get_refresh_token_expiry(cls) -> int:
        delta = timedelta(days=settings.jwt_refresh_token_expire_days)
        return int((datetime.now(UTC) + delta).timestamp())

    @classmethod
    def _get_access_token_expiry(cls) -> int:
        delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        return int((datetime.now(UTC) + delta).timestamp())
