from fastapi import status

from app.modules.tags.models import Tag, Taggable


class TestTagsAPI:
    async def test_create_tag(self, client, auth_headers, db_session):
        tag_data = {'name': 'Крипта', 'color': '#ff0000', 'scope': 'asset'}

        response = await client.post('/api/tags/', json=tag_data, headers=auth_headers)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data['name'] == tag_data['name']
        assert data['scope'] == 'asset'

    async def test_list_tags(self, client, auth_headers):
        tag_data = {'name': 'Крипта', 'scope': 'asset'}
        await client.post('/api/tags/', json=tag_data, headers=auth_headers)

        response = await client.get('/api/tags/', headers=auth_headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'Крипта'

    async def test_attach_tag_to_entity(self, client, auth_headers, db_session, user, save, asset):
        tag = await save(db_session, Tag(name='Крипта', scope='asset', user_id=user.id))

        response = await client.post(
            f'/api/tags/{tag.id}/entities/portfolio_asset/{asset.id}',
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        exists = await db_session.scalar(
            Taggable.__table__.select().where(
                Taggable.tag_id == tag.id,
                Taggable.entity_type == 'portfolio_asset',
                Taggable.entity_id == asset.id,
            ),
        )
        assert exists is not None

    async def test_attach_tag_to_foreign_entity_returns_404(
        self,
        client,
        auth_headers,
        db_session,
        user,
        save,
        foreign_asset,
    ):
        tag = await save(db_session, Tag(name='Крипта', scope='asset', user_id=user.id))

        response = await client.post(
            f'/api/tags/{tag.id}/entities/portfolio_asset/{foreign_asset.id}',
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_detach_tag_from_entity(self, client, auth_headers, db_session, user, save, asset):
        tag = await save(db_session, Tag(name='Крипта', scope='asset', user_id=user.id))
        await save(
            db_session,
            Taggable(tag_id=tag.id, entity_type='portfolio_asset', entity_id=asset.id),
        )

        response = await client.delete(
            f'/api/tags/{tag.id}/entities/portfolio_asset/{asset.id}',
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        exists = await db_session.scalar(
            Taggable.__table__.select().where(
                Taggable.tag_id == tag.id,
                Taggable.entity_type == 'portfolio_asset',
                Taggable.entity_id == asset.id,
            ),
        )
        assert exists is None

    async def test_attach_tag_invalid_entity_type(self, client, auth_headers, db_session, user, save):
        tag = await save(db_session, Tag(name='Крипта', scope='asset', user_id=user.id))

        response = await client.post(
            f'/api/tags/{tag.id}/entities/invalid_type/1',
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    async def test_update_tag(self, client, auth_headers, db_session, user, save):
        tag = await save(db_session, Tag(name='Крипта', scope='asset', user_id=user.id))

        response = await client.put(
            f'/api/tags/{tag.id}',
            json={'name': 'Криптовалюта'},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['name'] == 'Криптовалюта'

    async def test_delete_tag(self, client, auth_headers, db_session, user, save):
        tag = await save(db_session, Tag(name='Крипта', scope='asset', user_id=user.id))

        response = await client.delete(f'/api/tags/{tag.id}', headers=auth_headers)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        db_tag = await db_session.get(Tag, tag.id)
        assert db_tag is None
