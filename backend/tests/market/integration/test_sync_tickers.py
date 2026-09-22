"""Поведение sync_tickers на реальной базе.

Синхронизация переписана с пообъектных запросов на пакетные, поэтому проверяется
и результат, и число обращений к БД: регрессия обратно в N+1 должна ломать тест.
"""

from collections.abc import AsyncIterator

from sqlalchemy import event

from app.modules.market.models import Ticker, TickerExternalId, TickerIdentifier


def _pages(*pages: list[dict]) -> AsyncIterator[list[dict]]:
    async def _gen():
        for page in pages:
            yield page

    return _gen()


def _coin(ext_id: str, symbol: str, **extra) -> dict:
    return {'id': ext_id, 'name': symbol.upper(), 'symbol': symbol, **extra}


class TestSyncTickersBasics:
    async def test_creates_new_tickers(self, ticker_service, db_session, tickers):
        result = await ticker_service.sync_tickers(
            'crypto',
            _pages([_coin('btc', 'btc'), _coin('eth', 'eth')]),
            provider_name='CoinGecko',
        )

        assert result['created'] == 2
        rows = (await db_session.execute(Ticker.__table__.select())).fetchall()
        assert {r.symbol for r in rows} == {'btc', 'eth'}

    async def test_second_run_updates_instead_of_duplicating(self, ticker_service):
        page = [_coin('btc', 'btc'), _coin('eth', 'eth')]
        await ticker_service.sync_tickers('crypto', _pages(page), provider_name='CoinGecko')
        result = await ticker_service.sync_tickers('crypto', _pages(page), provider_name='CoinGecko')

        assert result['created'] == 0
        assert result['updated'] == 2

    async def test_strategy_used_skips_updates(self, ticker_service):
        page = [_coin('btc', 'btc')]
        await ticker_service.sync_tickers('crypto', _pages(page), provider_name='CoinGecko')
        result = await ticker_service.sync_tickers(
            'crypto',
            _pages(page),
            strategy='used',
            provider_name='CoinGecko',
        )

        assert result['updated'] == 0
        assert result['skipped'] == 1

    async def test_coin_without_id_is_ignored(self, ticker_service):
        result = await ticker_service.sync_tickers(
            'crypto',
            _pages([{'id': None, 'name': 'Broken'}, _coin('btc', 'btc')]),
            provider_name='CoinGecko',
        )

        assert result['created'] == 1

    async def test_null_fields_do_not_wipe_existing_values(self, ticker_service, db_session):
        await ticker_service.sync_tickers(
            'crypto',
            _pages([_coin('btc', 'btc', market_cap_rank=1)]),
            provider_name='CoinGecko',
        )
        # Провайдер временно отдаёт name/symbol как null — прежний .get(key, default)
        # затирал поле именно этим None.
        await ticker_service.sync_tickers(
            'crypto',
            _pages([{'id': 'btc', 'name': None, 'symbol': None}]),
            provider_name='CoinGecko',
        )
        await db_session.commit()

        ticker = (await db_session.execute(Ticker.__table__.select())).first()
        assert ticker.symbol == 'btc'
        assert ticker.name == 'BTC'


class TestSyncTickersIdentifiers:
    async def test_identifiers_persisted(self, ticker_service, db_session, extract_identifiers):
        coin = _coin('btc', 'btc', platforms={'ethereum': '0xabc'})
        await ticker_service.sync_tickers(
            'crypto',
            _pages([coin]),
            provider_name='CoinGecko',
            extract_identifiers=extract_identifiers,
        )
        await db_session.commit()

        rows = (await db_session.execute(TickerIdentifier.__table__.select())).fetchall()
        assert [(r.system, r.value) for r in rows] == [('contract_ethereum', '0xabc')]

    async def test_coin_matched_by_identifier_reuses_ticker(self, ticker_service, db_session, extract_identifiers):
        eth = _coin('ethereum', 'eth', platforms={'ethereum': '0xabc'})
        await ticker_service.sync_tickers(
            'crypto',
            _pages([eth]),
            provider_name='CoinGecko',
            extract_identifiers=extract_identifiers,
        )
        # Тот же контракт приходит от другого провайдера/символа — тикер переиспользуется.
        wrapped = _coin('weth', 'weth', platforms={'ethereum': '0xabc'})
        result = await ticker_service.sync_tickers(
            'crypto',
            _pages([wrapped]),
            provider_name='CoinGecko',
            extract_identifiers=extract_identifiers,
        )

        assert result['matched'] == 1
        assert result['created'] == 0
        await db_session.commit()
        assert len((await db_session.execute(Ticker.__table__.select())).fetchall()) == 1

    async def test_duplicate_identifier_inside_one_page_written_once(
        self, ticker_service, db_session, extract_identifiers
    ):
        coins = [
            _coin('a', 'aaa', platforms={'ethereum': '0xsame'}),
            _coin('b', 'bbb', platforms={'ethereum': '0xsame'}),
        ]
        result = await ticker_service.sync_tickers(
            'crypto',
            _pages(coins),
            provider_name='CoinGecko',
            extract_identifiers=extract_identifiers,
        )
        await db_session.commit()

        assert result['created'] == 2
        rows = (await db_session.execute(TickerIdentifier.__table__.select())).fetchall()
        assert len(rows) == 1


class TestSyncTickersExternalIds:
    async def test_external_ids_persisted(self, ticker_service, db_session):
        await ticker_service.sync_tickers(
            'crypto',
            _pages([_coin('btc', 'btc'), _coin('eth', 'eth')]),
            provider_name='CoinGecko',
        )
        await db_session.commit()

        rows = (await db_session.execute(TickerExternalId.__table__.select())).fetchall()
        assert {r.external_id for r in rows} == {'btc', 'eth'}
        assert {r.provider_name for r in rows} == {'CoinGecko'}

    async def test_external_id_reassigned_when_ticker_reused(self, ticker_service, db_session, extract_identifiers):
        await ticker_service.sync_tickers(
            'crypto',
            _pages([_coin('btc', 'btc', platforms={'ethereum': '0xabc'})]),
            provider_name='CoinGecko',
            extract_identifiers=extract_identifiers,
        )
        # Тот же контракт приходит с новым внешним id: тикер переиспользуется,
        # и external_id для него должен обновиться, а не задублироваться.
        await ticker_service.sync_tickers(
            'crypto',
            _pages([_coin('bitcoin', 'btc', platforms={'ethereum': '0xabc'})]),
            provider_name='CoinGecko',
            extract_identifiers=extract_identifiers,
        )
        await db_session.commit()

        rows = (await db_session.execute(TickerExternalId.__table__.select())).fetchall()
        assert [r.external_id for r in rows] == ['bitcoin']
        assert len((await db_session.execute(Ticker.__table__.select())).fetchall()) == 1


class TestQueryVolume:
    """Пакетная обработка: число запросов не должно расти с числом монет."""

    async def test_page_of_250_costs_a_constant_number_of_queries(
        self, ticker_service, db_session, extract_identifiers
    ):
        coins = [_coin(f'c{i}', f's{i}', platforms={'ethereum': f'0x{i:040x}'}) for i in range(250)]

        statements: list[str] = []

        def _record(conn, cursor, statement, params, context, executemany):
            statements.append(statement)

        event.listen(db_session.get_bind(), 'before_cursor_execute', _record)
        try:
            await ticker_service.sync_tickers(
                'crypto',
                _pages(coins),
                provider_name='CoinGecko',
                extract_identifiers=extract_identifiers,
            )
        finally:
            event.remove(db_session.get_bind(), 'before_cursor_execute', _record)

        inserts = [s for s in statements if s.lstrip().upper().startswith('INSERT')]
        selects = [s for s in statements if s.lstrip().upper().startswith('SELECT')]

        # 1 вставка тикеров + 1 external_id + 1 identifier + служебные.
        assert len(inserts) <= 3, f'ожидались пакетные вставки, получено {len(inserts)}'
        # Поиск существующих: тикеры, external_id, идентификаторы — константа.
        assert len(selects) <= 6, f'поиск вернулся к N+1: {len(selects)} SELECT на страницу'
