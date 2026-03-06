from unittest.mock import patch

import pytest
from shared.exceptions import BusinessRuleError, ConflictError, NotFoundError, PermissionDeniedError

from app.core import SecurityService
from app.repositories import UserRepository
from app.schemas import UserRole
from app.services import UserService

USER = UserRole.USER
MODERATOR = UserRole.MODERATOR
ADMIN = UserRole.ADMIN


@pytest.fixture
def service(db_session, async_mock, mock):
    return UserService(
        session=db_session,
        user_repo=async_mock(spec=UserRepository, session=db_session),
        security_service=mock(spec=SecurityService),
    )


class TestUserService:
    async def test_get_user_by_id_success(self, service, mock):
        user = mock(id=1)

        with patch.object(service.repo, 'get', return_value=user):
            result = await service.get(user.id)

            service.repo.get.assert_called_once_with(user.id)
            assert result == user

    async def test_get_user_by_id_not_found(self, service):
        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.get(999)

    async def test_get_user_by_email_success(self, service, mock):
        user = mock(email='test@example.com')

        with patch.object(service.repo, 'get_by_email', return_value=user):
            result = await service.get_by_email(user.email)

            service.repo.get_by_email.assert_called_once_with(user.email)
            assert result == user

    async def test_get_user_by_email_not_found(self, service):
        with (
            patch.object(service.repo, 'get_by_email', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.get_by_email('nonexistent@example.com')

    async def test_get_user_with_details_success(self, service, mock):
        user = mock(id=1)

        with patch.object(service.repo, 'get_with_sessions', return_value=user):
            result = await service.get_detailed(user.id)

            service.repo.get_with_sessions.assert_called_once_with(user.id)
            assert result == user

    async def test_get_user_with_details_not_found(self, service):
        with (
            patch.object(service.repo, 'get_with_sessions', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.get_detailed(999)

    async def test_create_user_success_no_current_user(self, service, mock, data):
        password_hash = 'hashed_password'
        create_data = data(email='test@example.com', password='Password123!', role=USER)
        user = mock(id=1)

        with (
            patch.object(service.repo, 'exists_by', return_value=False),
            patch.object(service.security, 'get_password_hash', return_value=password_hash),
            patch.object(service.repo, 'create', return_value=user),
        ):
            result = await service.create(create_data)

            service.security.get_password_hash.assert_called_once_with(create_data.password)
            service.repo.create.assert_called_once()

            call_args = service.repo.create.call_args
            user_create = call_args[0][0]
            assert user_create.email == create_data.email
            assert user_create.password_hash == password_hash
            assert user_create.role == USER

        service.session.flush.assert_called_once()
        assert result == user

    async def test_create_user_success_with_current_user_admin(self, service, mock, data):
        create_data = data(email='test@example.com', password='Password123!', role=USER)
        admin = mock(role=ADMIN, email='admin@example.com')
        user = mock()

        with (
            patch.object(service.repo, 'exists_by', return_value=False),
            patch.object(service.security, 'get_password_hash', return_value='hashed'),
            patch.object(service.repo, 'create', return_value=user),
        ):
            result = await service.create(create_data, actor=admin)

        assert result == user

    async def test_create_user_email_conflict(self, service, data):
        create_data = data(email='test@example.com', password='Password123!', role=USER)

        with (
            patch.object(service.repo, 'exists_by', return_value=True),
            pytest.raises(ConflictError, match='уже существует'),
        ):
            await service.create(create_data)

    @pytest.mark.parametrize(('current_role', 'target_role', 'should_raise'), [
        (None, USER, False),
        (None, ADMIN, True),
        (USER, ADMIN, True),
        (ADMIN, USER, False),
    ])
    async def test_create_user_role_validation(self, service, mock, data, current_role, target_role, should_raise):
        actor = mock(role=current_role) if current_role else None
        create_data = data(email='test@example.com', password='Password123!', role=target_role)

        with (
            patch.object(service.security, 'get_password_hash', return_value='hash'),
            patch.object(service.repo, 'create', return_value=mock()),
            patch.object(service.repo, 'exists_by', return_value=False),
        ):
            if should_raise:
                with pytest.raises(BusinessRuleError, match='права'):
                    await service.create(create_data, actor)
            else:
                result = await service.create(create_data, actor)

                assert result is not None
                service.repo.create.assert_called_once()
                service.security.get_password_hash.assert_called_once_with(create_data.password)

    async def test_update_user_success(self, service, mock, data):
        user_id = 1
        update_data = data(role=USER, status='active')
        user = mock(role=USER, email='user@example.com')
        updated_user = mock(role=USER, email='user@example.com')

        with (
            patch.object(service.repo, 'get', return_value=user),
            patch.object(service.security, 'get_password_hash', return_value='hash'),
            patch.object(service.repo, 'update', return_value=updated_user),
        ):
            result = await service.update(user_id, update_data, actor=user)

            service.repo.update.assert_called_once()
            assert result == updated_user

    async def test_update_user_not_found(self, service, mock, data):
        update_data = data(role=USER, status='active')
        user = mock(role=USER, email='user@example.com')

        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.update(999, update_data, actor=user)

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
    async def test_update_user_role_check(self, service, mock, data, current_role, target_role, should_raise, operation_for):
        update_data = data(role=USER, status='active')
        actor = mock(id=1, role=current_role)

        user_id = 1 if operation_for == 'self' else 2
        user_role = current_role if operation_for == 'self' else target_role
        user = mock(id=user_id, role=user_role)

        with (
            patch.object(service.repo, 'get', return_value=user),
            patch.object(service.security, 'get_password_hash', return_value='hash'),
            patch.object(service.repo, 'update', return_value=mock()),
        ):
            if should_raise:
                with pytest.raises(PermissionDeniedError):
                    await service.update(user_id, update_data, actor)
            else:
                result = await service.update(user_id, update_data, actor)

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
    async def test_update_user_role_validation(self, service, mock, data, current_role, target_role, should_raise, operation_for):
        update_data = data(role=target_role, status='active')
        actor = mock(id=1, role=current_role)

        user_id = 1 if operation_for == 'self' else 2
        user_role = current_role if operation_for == 'self' else target_role
        user = mock(id=user_id, role=user_role)

        with (
            patch.object(service.repo, 'get', return_value=user),
            patch.object(service.security, 'get_password_hash', return_value='hash'),
            patch.object(service.repo, 'update', return_value=mock()),
        ):
            if should_raise:
                with pytest.raises(BusinessRuleError):
                    await service.update(user_id, update_data, actor)
            else:
                result = await service.update(user_id, update_data, actor)

                assert result is not None

    async def test_delete_user_success(self, service, mock):
        user = mock(id=1)

        with (
            patch.object(service.repo, 'get', return_value=user),
            patch.object(service.repo, 'delete', return_value=True),
        ):
            await service.delete(user.id, actor=user)

            service.repo.delete.assert_called_once_with(user.id)

    async def test_delete_user_not_found(self, service, mock):
        with (
            patch.object(service.repo, 'get', return_value=None),
            pytest.raises(NotFoundError, match='не найден'),
        ):
            await service.delete(999, actor=mock(role=ADMIN))

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
    async def test_delete_user_role_check(self, service, mock, current_role, target_role, should_raise, operation_for):
        actor = mock(id=1, role=current_role)

        user_id = 1 if operation_for == 'self' else 2
        user = actor if operation_for == 'self' else mock(id=2, role=target_role)

        with (
            patch.object(service.repo, 'get', return_value=user),
        ):
            if should_raise:
                with pytest.raises(PermissionDeniedError):
                    await service.delete(user_id, actor)
            else:
                await service.delete(user_id, actor)

    async def test_update_user_activity_success(self, service):
        user_id = 1

        await service.update_activity(user_id)

        service.repo.update_activity.assert_called_once_with(user_id)
