import pytest

from app.models import LoginSession, RefreshToken
from app.repositories import SessionRepository, TokenRepository, UserRepository


class TestPublicAPI:
    """Тесты для публичных эндпоинтов."""

    @pytest.mark.asyncio
    async def test_service_info(self, client):
        """Тест получения информации о сервисе."""
        response = await client.get('/')

        assert response.status_code == 200
        data = response.json()
        assert '/docs' in data['docs']
        assert '/redoc' in data['redoc']

    @pytest.mark.asyncio
    async def test_register_success(self, client, db_session):
        """Полный тест удачной регистрации."""
        register_data = {'email': 'newuser@example.com', 'password': 'Password123!'}
        response = await client.post('/register', json=register_data)

        # Проверяем HTTP-ответ
        assert response.status_code == 201
        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

        # Проверяем что пользователь создан в БД
        repo = UserRepository(db_session)
        user = await repo.get_by_email('newuser@example.com')
        assert user is not None
        assert user.email == 'newuser@example.com'

        # Проверяем что refresh токен сохранен
        token_repo = TokenRepository(db_session)
        tokens = await token_repo.get_many_by(RefreshToken.user_id == user.id)
        assert len(tokens) == 1

        # Проверяем что создана сессия
        session_repo = SessionRepository(db_session)
        sessions = await session_repo.get_many_by(LoginSession.user_id == user.id)
        assert len(sessions) == 1

    @pytest.mark.asyncio
    async def test_login_success(self, client, db_session, test_user):
        """Полный тест удачного входа."""
        login_data = {'email': 'test@example.com', 'password': 'testpass'}
        response = await client.post('/login', json=login_data)

        # Проверяем HTTP-ответ
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

        # Проверяем что refresh токен сохранен
        token_repo = TokenRepository(db_session)
        tokens = await token_repo.get_many_by(RefreshToken.user_id == test_user.id)
        assert len(tokens) == 1

        # Проверяем что создана сессия
        session_repo = SessionRepository(db_session)
        sessions = await session_repo.get_many_by(LoginSession.user_id == test_user.id)
        assert len(sessions) == 1

    @pytest.mark.asyncio
    async def test_refresh_tokens_success(self, client, db_session, test_user):
        """Полный тест удачного обновления токенов."""
        # Входим для получения токена
        login_data = {'email': 'test@example.com', 'password': 'testpass'}
        response = await client.post('/login', json=login_data)

        # Получаем токен
        data = response.json()
        refresh_token = data['refresh_token']

        # Запрашиваем обновление токенов
        refresh_data = {'token': refresh_token}
        response = await client.post('/refresh', json=refresh_data)

        # Проверяем HTTP-ответ
        assert response.status_code == 200
        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data

        # Проверяем что refresh токен по прежнему один
        token_repo = TokenRepository(db_session)
        tokens = await token_repo.get_many_by(RefreshToken.user_id == test_user.id)
        assert len(tokens) == 1

        # Проверяем что сессия одна
        session_repo = SessionRepository(db_session)
        sessions = await session_repo.get_many_by(LoginSession.user_id == test_user.id)
        assert len(sessions) == 1
