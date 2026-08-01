from unittest.mock import patch

from app.modules.market.repositories import TickerIdentifierRepository


class TestTickerIdentifierRepository:
    async def test_upsert_all_creates_missing_only(self, db_session, mock):
        repo = TickerIdentifierRepository(db_session)
        with (
            patch.object(repo, 'find_by_identifiers', return_value={'gecko': mock()}) as find_by_identifiers,
            patch.object(repo, 'create_all', return_value=[]) as create_all,
        ):
            await repo.upsert_all(1, {'gecko': 'btc', 'cmc': 'btc-1'})
            find_by_identifiers.assert_awaited_once_with({'gecko': 'btc', 'cmc': 'btc-1'})
            create_all.assert_awaited_once_with(
                [{'ticker_id': 1, 'system': 'cmc', 'value': 'btc-1'}],
            )

    async def test_upsert_all_all_existing(self, db_session, mock):
        repo = TickerIdentifierRepository(db_session)
        with (
            patch.object(repo, 'find_by_identifiers', return_value={'gecko': mock(), 'cmc': mock()}) as find_by_identifiers,
            patch.object(repo, 'create_all', return_value=[]) as create_all,
        ):
            await repo.upsert_all(1, {'gecko': 'btc', 'cmc': 'btc-1'})
            find_by_identifiers.assert_awaited_once_with({'gecko': 'btc', 'cmc': 'btc-1'})
            create_all.assert_not_awaited()

    async def test_upsert_all_empty(self, db_session):
        repo = TickerIdentifierRepository(db_session)
        with patch.object(repo, 'find_by_identifiers') as find_by_identifiers:
            await repo.upsert_all(1, {})

        find_by_identifiers.assert_not_awaited()
