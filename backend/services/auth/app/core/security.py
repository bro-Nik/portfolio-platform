# TODO: Логирование для мониторинга атак.

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings as s
from app.core.exceptions import AuthenticationError
from app.schemas import UserSchema

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class SecurityService:
    """Сервис для работы с безопасностью и JWT токенами."""

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хэширует пароль с использованием bcrypt."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверяет соответствие пароля хэшу."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user: UserSchema) -> str:
        """Создает JWT access токен для пользователя."""
        exp = SecurityService._expires_timestamp(timedelta(minutes=s.access_token_expire_minutes))
        payload: dict[str, Any] = {
            'sub': str(user.id),
            'login': user.email.split('@')[0],
            'role': user.role,
            'type': 'access',
            'exp': exp,
        }

        return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)

    @staticmethod
    def create_refresh_token(user: UserSchema) -> str:
        """Создает JWT refresh токен для пользователя."""
        exp = SecurityService._expires_timestamp(timedelta(days=s.refresh_token_expire_days))
        payload: dict[str, Any] = {
            'sub': str(user.id),
            'type': 'refresh',
            'exp': exp,
        }

        return jwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)

    @staticmethod
    def verify_token(token: str) -> dict[str, Any]:
        """Верифицирует JWT токен. Возвращает payload или выбрасывает исключение."""
        try:
            return jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm])
        except jwt.ExpiredSignatureError as e:
            raise AuthenticationError('Токен устарел') from e
        except jwt.InvalidTokenError as e:
            raise AuthenticationError('Некорректный токен') from e
        except jwt.PyJWTError as e:
            # Обработка любых других ошибок PyJWT
            raise AuthenticationError('Ошибка верификации токена') from e

    @staticmethod
    def is_token_expired(expires_at: int) -> bool:
        """Проверяет истек ли токен по timestamp."""
        return datetime.now(UTC).timestamp() > expires_at

    @staticmethod
    def _expires_timestamp(delta: timedelta) -> int:
        """Timestamp сейчас + delta."""
        date = datetime.now(UTC) + delta
        return int(date.timestamp())
