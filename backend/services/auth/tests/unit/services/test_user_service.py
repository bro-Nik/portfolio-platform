from unittest.mock import MagicMock, patch

import pytest
from shared.exceptions import BusinessRuleError, ConflictError, NotFoundError, PermissionDeniedError

from app.schemas import UserCreateRequest, UserRole, UserUpdateRequest
from app.services import UserService

USER = UserRole.USER
MODERATOR = UserRole.MODERATOR
ADMIN = UserRole.ADMIN


@pytest.fixture
def service(mock_async_session, mock_user_repo, mock_security_service):
    return UserService(
        session=mock_async_session,
        user_repo=mock_user_repo,
        security_service=mock_security_service,
    )

@pytest.fixture
def user_create_request():
    return UserCreateRequest(
        email='test@example.com',
        password='Password123!',
        role=USER,
        status='active',
    )

@pytest.fixture
def user_update_request():
    return UserUpdateRequest(role=USER, status='active')


class TestUserService:
    async def test_get_user_by_id_success(self, service, mock_db_user):
        user_id = 1

        with patch.object(service.repo, 'get', return_value=mock_db_user):
            result = await service.get(user_id)

            service.repo.get.assert_called_once_with(user_id)
            assert result == mock_db_user

    async def test_get_user_by_id_not_found(self, service):
        user_id = 999

        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.get(user_id)

    async def test_get_user_by_email_success(self, service, mock_db_user):
        email = 'test@example.com'

        with patch.object(service.repo, 'get_by_email', return_value=mock_db_user):
            result = await service.get_by_email(email)

            service.repo.get_by_email.assert_called_once_with(email)
            assert result == mock_db_user

    async def test_get_user_by_email_not_found(self, service):
        email = 'nonexistent@example.com'

        with (
            patch.object(service.repo, 'get_by_email', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.get_by_email(email)

    async def test_get_user_with_details_success(self, service, mock_db_user):
        user_id = 1

        with patch.object(service.repo, 'get_with_sessions', return_value=mock_db_user):
            result = await service.get_detailed(user_id)

            service.repo.get_with_sessions.assert_called_once_with(user_id)
            assert result == mock_db_user

    async def test_get_user_with_details_not_found(self, service):
        user_id = 999

        with (
            patch.object(service.repo, 'get_with_sessions', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.get_detailed(user_id)

    async def test_create_user_success_no_current_user(self, service, user_create_request, mock_db_user):
        password_hash = 'hashed_password'

        with (
            patch.object(service.repo, 'exists_by', return_value=False),
            patch.object(service.security, 'get_password_hash', return_value=password_hash),
            patch.object(service.repo, 'create', return_value=mock_db_user),
        ):
            result = await service.create(user_create_request)

            service.security.get_password_hash.assert_called_once_with('Password123!')
            service.repo.create.assert_called_once()

            # Проверяем что передается UserCreate с хэшем пароля
            call_args = service.repo.create.call_args
            user_create = call_args[0][0]
            assert user_create.email == 'test@example.com'
            assert user_create.password_hash == password_hash
            assert user_create.role == USER

        service.session.flush.assert_called_once()
        assert result == mock_db_user

    async def test_create_user_success_with_current_user_admin(self, service, user_create_request, mock_admin, mock_db_user):
        with (
            patch.object(service.repo, 'exists_by', return_value=False),
            patch.object(service.security, 'get_password_hash', return_value='hashed'),
            patch.object(service.repo, 'create', return_value=mock_db_user),
        ):
            result = await service.create(user_create_request, actor=mock_admin)

        assert result == mock_db_user

    async def test_create_user_email_conflict(self, service, user_create_request):
        with (
            patch.object(service.repo, 'exists_by', return_value=True),
            pytest.raises(ConflictError, match='уже существует'),
        ):
            await service.create(user_create_request)

    @pytest.mark.parametrize(('current_role', 'target_role', 'should_raise'), [
        (None, USER, False),
        (None, ADMIN, True),
        (USER, ADMIN, True),
        (ADMIN, USER, False),
    ])
    async def test_create_user_role_validation(self, service, user_create_request, current_role, target_role, should_raise):
        actor = MagicMock(role=current_role) if current_role else None
        user_create_request.role = target_role

        with (
            patch.object(service.security, 'get_password_hash', return_value='hash'),
            patch.object(service.repo, 'create', return_value=MagicMock()),
            patch.object(service.repo, 'exists_by', return_value=False),
        ):
            if should_raise:
                with pytest.raises(BusinessRuleError, match='права'):
                    await service.create(user_create_request, actor)
            else:
                result = await service.create(user_create_request, actor)

                assert result is not None
                service.repo.create.assert_called_once()
                service.security.get_password_hash.assert_called_once_with('Password123!')

    async def test_update_user_success(self, service, user_update_request, mock_db_user, mock_user):
        user_id = 1  # ID обычного пользователя

        with (
            patch.object(service.repo, 'get', return_value=mock_db_user),
            patch.object(service.security, 'get_password_hash', return_value='hash'),
            patch.object(service.repo, 'update', return_value=mock_db_user),
        ):
            result = await service.update(user_id, user_update_request, actor=mock_user)

            service.repo.update.assert_called_once()
            assert result == mock_db_user

    async def test_update_user_not_found(self, service, user_update_request, mock_admin):
        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.update(999, user_update_request, actor=mock_admin)

    @pytest.mark.parametrize(('current_role', 'target_role', 'should_raise', 'operation_for'), [
        (USER, USER, False, 'self'),  # Сам себя - можно
        (MODERATOR, MODERATOR, False, 'self'),
        (ADMIN, ADMIN, False, 'self'),
        (USER, USER, True, 'other'),  # Другого - можно, если у обновляемого роль ниже
        (USER, ADMIN, True, 'other'),
        (MODERATOR, USER, False, 'other'),
        (MODERATOR, MODERATOR, True, 'other'),
        (MODERATOR, ADMIN, True, 'other'),
        (ADMIN, USER, False, 'other'),
        (ADMIN, MODERATOR, False, 'other'),
        (ADMIN, ADMIN, True, 'other'),
    ])
    async def test_update_user_role_check(self, service, user_update_request, current_role, target_role, should_raise, operation_for):
        actor = MagicMock(id=1, role=current_role)

        target_user_id = 1 if operation_for == 'self' else 2
        target_user_role = current_role if operation_for == 'self' else target_role
        target_user = MagicMock(id=target_user_id, role=target_user_role)

        with (
            patch.object(service.repo, 'get', return_value=target_user),
            patch.object(service.security, 'get_password_hash', return_value='hash'),
            patch.object(service.repo, 'update', return_value=MagicMock()),
        ):
            if should_raise:
                with pytest.raises(PermissionDeniedError):
                    await service.update(target_user_id, user_update_request, actor)
            else:
                result = await service.update(target_user_id, user_update_request, actor)

                assert result is not None

    @pytest.mark.parametrize(('current_role', 'target_role', 'should_raise', 'operation_for'), [
        (USER, USER, False, 'self'),  # Сам себя - роль не выше своей
        (USER, ADMIN, True, 'self'),
        (MODERATOR, MODERATOR, False, 'self'),
        (MODERATOR, ADMIN, True, 'self'),
        (MODERATOR, USER, False, 'self'),
        (ADMIN, ADMIN, False, 'self'),
        (ADMIN, MODERATOR, False, 'self'),
        (MODERATOR, USER, False, ''),  # Другого - только роль ниже своей
        (ADMIN, USER, False, ''),
        (ADMIN, MODERATOR, False, ''),
    ])
    async def test_update_user_role_validation(self, service, user_update_request, current_role, target_role, should_raise, operation_for):
        actor = MagicMock(id=1, role=current_role)

        target_user_id = 1 if operation_for == 'self' else 2
        target_user_role = current_role if operation_for == 'self' else target_role
        target_user = MagicMock(id=target_user_id, role=target_user_role)

        user_update_request.role = target_role

        with (
            patch.object(service.repo, 'get', return_value=target_user),
            patch.object(service.security, 'get_password_hash', return_value='hash'),
            patch.object(service.repo, 'update', return_value=MagicMock()),
        ):
            if should_raise:
                with pytest.raises(BusinessRuleError):
                    await service.update(target_user_id, user_update_request, actor)
            else:
                result = await service.update(target_user_id, user_update_request, actor)

                assert result is not None

    async def test_delete_user_success(self, service, mock_db_user, mock_user):
        user_id = 1

        with (
            patch.object(service.repo, 'get', return_value=mock_db_user),
            patch.object(service.repo, 'delete', return_value=True),
        ):
            await service.delete(user_id, actor=mock_user)

            service.repo.delete.assert_called_once_with(user_id)

    async def test_delete_user_not_found(self, service, mock_admin):
        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.delete(999, actor=mock_admin)

    @pytest.mark.parametrize(('current_role', 'target_role', 'should_raise', 'operation_for'), [
        (USER, USER, False, 'self'),  # Сам себя - можно
        (MODERATOR, MODERATOR, False, 'self'),
        (ADMIN, ADMIN, False, 'self'),
        (USER, USER, True, 'other'),  # Другого - можно, если роль удаляемого ниже
        (USER, ADMIN, True, 'other'),
        (MODERATOR, USER, False, 'other'),
        (MODERATOR, MODERATOR, True, 'other'),
        (MODERATOR, ADMIN, True, 'other'),
        (ADMIN, USER, False, 'other'),
        (ADMIN, MODERATOR, False, 'other'),
        (ADMIN, ADMIN, True, 'other'),
    ])
    async def test_delete_user_role_check(self, service, current_role, target_role, should_raise, operation_for):
        actor = MagicMock(id=1, role=current_role)

        target_user_id = 1 if operation_for == 'self' else 2
        target_user = actor if operation_for == 'self' else MagicMock(id=2, role=target_role)

        with (
            patch.object(service.repo, 'get', return_value=target_user),
        ):
            if should_raise:
                with pytest.raises(PermissionDeniedError):
                    await service.delete(target_user_id, actor)
            else:
                await service.delete(target_user_id, actor)

    async def test_update_user_activity_success(self, service):
        user_id = 1

        await service.update_activity(user_id)

        service.repo.update_activity.assert_called_once_with(user_id)
