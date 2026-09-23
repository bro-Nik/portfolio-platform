"""Границы пагинации на списочных эндпоинтах.

Без них `pageSize` и `limit` были просто числами: admin-эндпоинт тикеров
принимал pageSize=10000000 и пытался материализовать столько ORM-объектов.
"""

from fastapi import status
import pytest

from app.common.pagination import DEFAULT_PAGE_SIZE, MAX_ADMIN_PAGE_SIZE, MAX_PAGE_SIZE


class TestTickerSearchPagination:
    @pytest.mark.parametrize('page_size', [0, -1, MAX_PAGE_SIZE + 1, 10**7])
    async def test_rejects_out_of_range_page_size(self, market_client, auth_headers, page_size):
        response = await market_client.get(
            '/market/api/tickers',
            params={'pageSize': page_size},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize('page', [0, -5])
    async def test_rejects_non_positive_page(self, market_client, auth_headers, page):
        response = await market_client.get('/market/api/tickers', params={'page': page}, headers=auth_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_accepts_max_page_size(self, market_client, auth_headers):
        response = await market_client.get(
            '/market/api/tickers',
            params={'pageSize': MAX_PAGE_SIZE},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK


class TestAdminTickerListPagination:
    @pytest.mark.parametrize('page_size', [0, MAX_ADMIN_PAGE_SIZE + 1, 10**7])
    async def test_rejects_out_of_range_page_size(self, market_client, admin_headers, page_size):
        response = await market_client.get(
            '/market/admin/tickers',
            params={'pageSize': page_size},
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_accepts_max_page_size(self, market_client, admin_headers):
        response = await market_client.get(
            '/market/admin/tickers',
            params={'pageSize': MAX_ADMIN_PAGE_SIZE},
            headers=admin_headers,
        )

        assert response.status_code == status.HTTP_200_OK


class TestAdminUserListPagination:
    @pytest.mark.parametrize('limit', [0, MAX_ADMIN_PAGE_SIZE + 1])
    async def test_rejects_out_of_range_limit(self, market_client, admin_headers, limit):
        response = await market_client.get('/auth/admin/users', params={'limit': limit}, headers=admin_headers)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestPaginationContract:
    def test_defaults_are_shared(self):
        # Значения по умолчанию разъезжались между эндпоинтами: 20, 100, 1000.
        assert DEFAULT_PAGE_SIZE == 20
        assert MAX_PAGE_SIZE >= DEFAULT_PAGE_SIZE
        assert MAX_ADMIN_PAGE_SIZE >= MAX_PAGE_SIZE
