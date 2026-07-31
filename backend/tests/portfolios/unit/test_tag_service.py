from unittest.mock import patch

import pytest

from app.common.exceptions import NotFoundError
from app.modules.portfolios.repositories import TagRepository
from app.modules.portfolios.services.tag import TagService

user_id = 1


@pytest.fixture
async def service(db_session, async_mock, data):
    ctx = data(actor=data(id=user_id))
    service = TagService(db_session, ctx)
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
            create.assert_called_once_with({
                'name': 'X', 'color': '#1890ff', 'scope': 'wallet', 'user_id': user_id,
            })

    async def test_create_default_scope(self, service, mock):
        tag = mock(id=1, name='X', color=None, scope='asset', user_id=user_id)

        with patch.object(service.repo, 'create', return_value=tag) as create:
            result = await service.create('X')

            assert result == tag
            create.assert_called_once_with({
                'name': 'X', 'color': None, 'scope': 'asset', 'user_id': user_id,
            })

    async def test_update_foreign_tag_raises(self, service, mock):
        tag = mock(id=1, name='X', color=None, scope='portfolio', user_id=999)

        with patch.object(service.repo, 'get', return_value=tag):
            with pytest.raises(NotFoundError):
                await service.update(1, name='Y')

    async def test_delete_foreign_tag_raises(self, service, mock):
        tag = mock(id=1, name='X', color=None, scope='portfolio', user_id=999)

        with patch.object(service.repo, 'get', return_value=tag):
            with pytest.raises(NotFoundError):
                await service.delete(1)
