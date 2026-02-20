"""Фикстуры для UNIT-тестов."""

from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from app.core.security import SecurityService
from app.repositories import SessionRepository, TokenRepository, UserRepository
from app.schemas import UserLogin, UserRole, UserSchema
from app.services.user import UserService


@pytest.fixture
def mock_async_session() -> AsyncMock:
    """Мок асинхронной сессии БД для unit-тестов."""
    session = AsyncMock()

    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()

    # Для работы с контекстным менеджером
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    return session


@pytest.fixture
def mock_login_data() -> UserLogin:
    """Данные для входа пользователя."""
    return UserLogin(email='test@example.com', password='password123')


@pytest.fixture
def mock_user() -> UserSchema:
    """Мок пользователя USER роли."""
    return UserSchema(id=1, role=UserRole.USER, email='user@example.com')


@pytest.fixture
def mock_admin() -> UserSchema:
    """Мок пользователя ADMIN роли."""
    return UserSchema(id=2, role=UserRole.ADMIN, email='admin@example.com')


@pytest.fixture
def mock_moderator() -> UserSchema:
    """Мок пользователя MODERATOR роли."""
    return UserSchema(id=3, role=UserRole.MODERATOR, email='moderator@example.com')


@pytest.fixture
def mock_token_repo(mock_async_session) -> MagicMock:
    """Мок репозитория токенов."""
    repo = MagicMock(spec=TokenRepository)
    repo.session = mock_async_session

    repo.get_by_token = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.delete_user_tokens = AsyncMock()
    repo.get = AsyncMock()
    repo.get_by = AsyncMock()

    return repo


@pytest.fixture
def mock_user_repo(mock_async_session) -> MagicMock:
    """Мок репозитория пользователей."""
    repo = MagicMock(spec=UserRepository)
    repo.session = mock_async_session

    repo.get_by_email = AsyncMock()
    repo.get = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.update_activity = AsyncMock()
    repo.exists_by = AsyncMock()

    return repo


@pytest.fixture
def mock_session_repo(mock_async_session) -> MagicMock:
    """Мок репозитория сессий."""
    repo = MagicMock(spec=SessionRepository)
    repo.session = mock_async_session

    repo.get_by_token_id = AsyncMock()
    repo.create = AsyncMock()
    repo.update = AsyncMock()

    return repo


@pytest.fixture
def mock_user_service(mock_async_session, mock_user_repo) -> MagicMock:
    """Мок сервиса пользователей."""
    service = MagicMock(spec=UserService)
    service.session = mock_async_session
    service.repo = mock_user_repo

    service.get_user_by_email = AsyncMock()
    service.get_user_by_id = AsyncMock()
    service.create_user = AsyncMock()
    service.update_user = AsyncMock()
    service.delete_user = AsyncMock()
    service.update_user_activity = AsyncMock()

    return service


@pytest.fixture
def mock_security_service() -> MagicMock:
    """Мок сервиса безопасности."""
    service = MagicMock(spec=SecurityService)

    service.get_password_hash = Mock()
    service.verify_password = Mock()
    service.create_access_token = Mock()
    service.create_refresh_token = Mock()
    service.verify_token = Mock()
    service.is_token_expired = Mock()

    return service


@pytest.fixture
def mock_db_user() -> MagicMock:
    """Мок SQLAlchemy модели User."""
    user = MagicMock()
    user.id = 1
    user.email = 'test@example.com'
    user.password_hash = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'
    user.role = UserRole.USER
    user.is_active = True
    user.created_at = None
    user.last_active_at = None
    user.total_active_time = 0
    user.status = 'active'

    return user


@pytest.fixture
def mock_db_token() -> MagicMock:
    """Мок SQLAlchemy модели RefreshToken."""
    token = MagicMock()
    token.id = 100
    token.user_id = 1
    token.token = 'refresh.token.value'
    token.expires_at = 9999999999

    return token


@pytest.fixture
def mock_request() -> MagicMock:
    """Мок FastAPI Request объекта."""
    request = MagicMock()

    request.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'x-real-ip': '192.168.1.1',
        'x-forwarded-for': '10.0.0.1, 192.168.1.1',
    }

    return request
