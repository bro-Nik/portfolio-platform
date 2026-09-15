from unittest.mock import AsyncMock, patch

import pytest

from app.common.exceptions import NotFoundError
from app.modules.tags.protocols import EntityOwnershipChecker
from app.modules.tags.repositories import TagRepository
from app.modules.tags.services.tag import TagService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    ownership = async_mock(spec=EntityOwnershipChecker)
    ownership.owns_entity = AsyncMock(return_value=True)
    service = TagService(db_session, ctx, ownership=ownership)
    service.repo = async_mock(spec=TagRepository, session=db_session)
    service.taggable_repo = async_mock()
    return service


class TestTagService:
    async def test_get_all(self, service, mock):
        tags = [mock(id=1, name='A', scope='portfolio', user_id=user_id)]

        with patch.object(service.repo, 'get_by_user', return_value=tags) as get_by_user:
            result = await service.get_all()

            assert result == tags
            get_by_user.assert_called_once_with(user_id)

    async def test_create_with_scope(self, service, mock):
        tag = mock(id=1, name='X', color='#1890ff', scope='wallet', user_id=user_id)

        with patch.object(service.repo, 'create', return_value=tag) as create:
            result = await service.create('X', '#1890ff', 'wallet')

            assert result == tag
            create.assert_called_once_with(
                {
                    'name': 'X',
                    'color': '#1890ff',
                    'scope': 'wallet',
                    'user_id': user_id,
                }
            )

    async def test_create_default_scope(self, service, mock):
        tag = mock(id=1, name='X', color=None, scope='asset', user_id=user_id)

        with patch.object(service.repo, 'create', return_value=tag) as create:
            result = await service.create('X')

            assert result == tag
            create.assert_called_once_with(
                {
                    'name': 'X',
                    'color': None,
                    'scope': 'asset',
                    'user_id': user_id,
                }
            )

    async def test_update_foreign_tag_raises(self, service, mock):
        tag = mock(id=1, name='X', color=None, scope='portfolio', user_id=999)

        with patch.object(service.repo, 'get', return_value=tag), pytest.raises(NotFoundError):
            await service.update(1, name='Y')

    async def test_delete_foreign_tag_raises(self, service, mock):
        tag = mock(id=1, name='X', color=None, scope='portfolio', user_id=999)

        with patch.object(service.repo, 'get', return_value=tag), pytest.raises(NotFoundError):
            await service.delete(1)

    async def test_add_to_entity_skips_when_already_attached(self, service, mock):
        tag = mock(id=1, name='X', scope='portfolio', user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=tag),
            patch.object(service.taggable_repo, 'exists', return_value=True) as exists,
            patch.object(service.taggable_repo, 'add') as add,
        ):
            await service.add_to_entity(1, 'portfolio', 5)

            exists.assert_awaited_once_with(1, 'portfolio', 5)
            add.assert_not_called()

    async def test_add_to_entity_attaches_when_missing(self, service, mock):
        tag = mock(id=1, name='X', scope='portfolio', user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=tag),
            patch.object(service.taggable_repo, 'exists', return_value=False),
            patch.object(service.taggable_repo, 'add') as add,
        ):
            await service.add_to_entity(1, 'portfolio', 5)

            add.assert_called_once_with(1, 'portfolio', 5)

    async def test_add_to_entity_rejects_foreign_entity(self, service, mock):
        tag = mock(id=1, name='X', scope='portfolio', user_id=user_id)
        service._ownership.owns_entity = AsyncMock(return_value=False)

        with (
            patch.object(service.repo, 'get', return_value=tag),
            patch.object(service.taggable_repo, 'exists', return_value=False) as exists,
            patch.object(service.taggable_repo, 'add') as add,
        ):
            with pytest.raises(NotFoundError):
                await service.add_to_entity(1, 'portfolio', 5)

            exists.assert_not_called()
            add.assert_not_called()

    async def test_remove_from_entity_checks_tag_ownership(self, service, mock):
        foreign_tag = mock(id=1, name='X', scope='portfolio', user_id=999)

        with (
            patch.object(service.repo, 'get', return_value=foreign_tag),
            patch.object(service.taggable_repo, 'remove') as remove,
        ):
            with pytest.raises(NotFoundError):
                await service.remove_from_entity(1, 'portfolio', 5)

            remove.assert_not_called()

    async def test_remove_from_entity_checks_entity_ownership(self, service, mock):
        tag = mock(id=1, name='X', scope='portfolio', user_id=user_id)
        service._ownership.owns_entity = AsyncMock(return_value=False)

        with (
            patch.object(service.repo, 'get', return_value=tag),
            patch.object(service.taggable_repo, 'remove') as remove,
        ):
            with pytest.raises(NotFoundError):
                await service.remove_from_entity(1, 'portfolio', 5)

            remove.assert_not_called()

    async def test_remove_from_entity_detaches_own_tag_and_entity(self, service, mock):
        tag = mock(id=1, name='X', scope='portfolio', user_id=user_id)

        with (
            patch.object(service.repo, 'get', return_value=tag),
            patch.object(service.taggable_repo, 'remove') as remove,
        ):
            await service.remove_from_entity(1, 'portfolio', 5)

            service._ownership.owns_entity.assert_awaited_once_with('portfolio', 5, user_id)
            remove.assert_called_once_with(1, 'portfolio', 5)
