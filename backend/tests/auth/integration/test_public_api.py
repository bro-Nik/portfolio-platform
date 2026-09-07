from app.modules.auth.models import LoginSession, RefreshToken
from app.modules.auth.repositories import SessionRepository, TokenRepository, UserRepository


class TestPublicAPI:
    async def test_service_info(self, client):
        response = await client.get('/')

        assert response.status_code == 200
        data = response.json()
        assert '/docs' in data['docs']
        assert '/redoc' in data['redoc']

    async def test_register_success(self, client, db_session):
        register_data = {'email': 'newuser@example.com', 'password': 'Password123!'}
        response = await client.post('/auth/register', json=register_data)

        assert response.status_code == 201
        data = response.json()
        assert 'accessToken' in data
        assert 'refreshToken' not in data

        set_cookie = response.headers.get('set-cookie', '')
        assert 'refresh_token=' in set_cookie
        assert 'httponly' in set_cookie.lower()
        assert 'samesite=strict' in set_cookie.lower()

        repo = UserRepository(db_session)
        user = await repo.get_by_email('newuser@example.com')
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.is_verified is False

        token_repo = TokenRepository(db_session)
        tokens = await token_repo.get_all(RefreshToken.user_id == user.id)
        assert len(tokens) == 1

        session_repo = SessionRepository(db_session)
        sessions = await session_repo.get_all(LoginSession.user_id == user.id)
        assert len(sessions) == 1

    async def test_login_success(self, client, db_session, test_user):
        login_data = {'email': 'test@example.com', 'password': 'testpass'}
        response = await client.post('/auth/login', json=login_data)

        assert response.status_code == 200
        data = response.json()
        assert 'accessToken' in data
        assert 'refreshToken' not in data
        assert 'refresh_token=' in response.headers.get('set-cookie', '')

        token_repo = TokenRepository(db_session)
        tokens = await token_repo.get_all(RefreshToken.user_id == test_user.id)
        assert len(tokens) == 1

        session_repo = SessionRepository(db_session)
        sessions = await session_repo.get_all(LoginSession.user_id == test_user.id)
        assert len(sessions) == 1

    async def test_refresh_tokens_success(self, client, db_session, test_user):
        login_data = {'email': 'test@example.com', 'password': 'testpass'}
        response = await client.post('/auth/login', json=login_data)

        assert 'refresh_token=' in response.headers.get('set-cookie', '')

        response = await client.post('/auth/refresh')

        assert response.status_code == 200
        data = response.json()
        assert 'accessToken' in data
        assert 'refreshToken' not in data

        token_repo = TokenRepository(db_session)
        tokens = await token_repo.get_all(RefreshToken.user_id == test_user.id)
        assert len(tokens) == 1

        session_repo = SessionRepository(db_session)
        sessions = await session_repo.get_all(LoginSession.user_id == test_user.id)
        assert len(sessions) == 1

    async def test_refresh_without_cookie_fails(self, client, test_user):
        response = await client.post('/auth/refresh')

        assert response.status_code == 401

    async def test_logout_revokes_and_clears_cookie(self, client, db_session, test_user):
        login_data = {'email': 'test@example.com', 'password': 'testpass'}
        await client.post('/auth/login', json=login_data)

        response = await client.post('/auth/logout')

        assert response.status_code == 204
        set_cookie = response.headers.get('set-cookie', '')
        assert 'refresh_token=' in set_cookie
        assert 'max-age=0' in set_cookie.lower() or 'expires=thu, 01 jan 1970' in set_cookie.lower()

        token_repo = TokenRepository(db_session)
        tokens = await token_repo.get_all(RefreshToken.user_id == test_user.id)
        assert len(tokens) == 0
