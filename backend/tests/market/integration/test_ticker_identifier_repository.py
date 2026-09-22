"""Поведение репозитория идентификаторов тикеров на реальной базе.

Семантика конфликтов (пара (system, value) принадлежит первому тикеру и не
переназначается) обеспечивается ON CONFLICT DO NOTHING в SQL, поэтому её и
проверяем через настоящие вставки, а не через замоканные вызовы.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy import func, select

from app.modules.market.models import Ticker, TickerIdentifier
from app.modules.market.repositories import TickerIdentifierRepository


@pytest.fixture
def repo(db_session):
    return TickerIdentifierRepository(db_session)


@pytest.fixture
async def seeded_tickers(db_session):
    rows = [
        Ticker(name=name, symbol=symbol, market='crypto', price=0.0, updated_at=datetime.now(UTC))
        for name, symbol in (('Bitcoin', 'BTC'), ('Ethereum', 'ETH'))
    ]
    db_session.add_all(rows)
    await db_session.flush()
    return {row.symbol: row.id for row in rows}


async def _count(session) -> int:
    return (await session.execute(select(func.count()).select_from(TickerIdentifier))).scalar_one()


class TestInsertMany:
    async def test_empty_is_noop(self, repo, db_session, seeded_tickers):
        assert await repo.insert_many([]) == 0
        assert await _count(db_session) == 0

    async def test_inserts_all_pairs(self, repo, db_session, seeded_tickers):
        inserted = await repo.insert_many(
            [
                {'ticker_id': seeded_tickers['BTC'], 'system': 'gecko', 'value': 'btc'},
                {'ticker_id': seeded_tickers['BTC'], 'system': 'cmc', 'value': 'btc-1'},
            ]
        )
        await db_session.commit()

        assert inserted == 2
        assert await _count(db_session) == 2

    async def test_existing_pair_is_not_reassigned(self, repo, db_session, seeded_tickers):
        await repo.insert_many([{'ticker_id': seeded_tickers['BTC'], 'system': 'gecko', 'value': 'btc'}])
        await db_session.commit()

        await repo.insert_many(
            [
                {'ticker_id': seeded_tickers['ETH'], 'system': 'gecko', 'value': 'btc'},
                {'ticker_id': seeded_tickers['ETH'], 'system': 'cmc', 'value': 'btc-1'},
            ]
        )
        await db_session.commit()

        rows = (await db_session.execute(select(TickerIdentifier))).scalars().all()
        by_system = {r.system: r.ticker_id for r in rows}
        assert by_system == {'gecko': seeded_tickers['BTC'], 'cmc': seeded_tickers['ETH']}

    async def test_same_value_in_batch_is_written_once(self, repo, db_session, seeded_tickers):
        # Страница провайдера может содержать дубли: (system, value) уникален.
        inserted = await repo.insert_many(
            [
                {'ticker_id': seeded_tickers['BTC'], 'system': 'gecko', 'value': 'dup'},
                {'ticker_id': seeded_tickers['ETH'], 'system': 'gecko', 'value': 'dup'},
            ]
        )
        await db_session.commit()

        assert inserted == 1
        assert await _count(db_session) == 1


class TestUpsertAll:
    async def test_empty_identifiers_noop(self, repo, db_session, seeded_tickers):
        await repo.upsert_all(seeded_tickers['BTC'], {})
        assert await _count(db_session) == 0

    async def test_writes_pairs(self, repo, db_session, seeded_tickers):
        await repo.upsert_all(seeded_tickers['BTC'], {'gecko': 'btc', 'cmc': 'btc-1'})
        await db_session.commit()

        assert await _count(db_session) == 2


class TestFindTickerIdsByPairs:
    async def test_empty(self, repo, seeded_tickers):
        assert await repo.find_ticker_ids_by_pairs(set()) == {}

    async def test_finds_across_tickers(self, repo, db_session, seeded_tickers):
        await repo.insert_many(
            [
                {'ticker_id': seeded_tickers['BTC'], 'system': 'gecko', 'value': 'btc'},
                {'ticker_id': seeded_tickers['ETH'], 'system': 'cmc', 'value': 'eth-1'},
            ]
        )
        await db_session.commit()

        result = await repo.find_ticker_ids_by_pairs({('gecko', 'btc'), ('cmc', 'eth-1')})

        assert result == {('gecko', 'btc'): seeded_tickers['BTC'], ('cmc', 'eth-1'): seeded_tickers['ETH']}

    async def test_ignores_unknown_pairs(self, repo, db_session, seeded_tickers):
        await repo.insert_many([{'ticker_id': seeded_tickers['BTC'], 'system': 'gecko', 'value': 'btc'}])
        await db_session.commit()

        result = await repo.find_ticker_ids_by_pairs({('gecko', 'btc'), ('gecko', 'nope')})

        assert result == {('gecko', 'btc'): seeded_tickers['BTC']}
