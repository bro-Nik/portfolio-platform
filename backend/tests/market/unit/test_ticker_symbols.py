from app.modules.market.repositories import TickerRepository
from app.modules.market.services.ticker import TickerService
from app.modules.market.services.ticker_external_id import TickerExternalIdService
from app.modules.market.services.ticker_identifier import TickerIdentifierService


def make_service(db_session, async_mock):
    return TickerService(
        db_session,
        repo=async_mock(spec=TickerRepository, session=db_session),
        ext_id_service=async_mock(spec=TickerExternalIdService),
        identifier_service=async_mock(spec=TickerIdentifierService),
    )


class TestResolvePricesBySymbol:
    async def test_resolves_iso_keys_to_ticker_ids(self, db_session, async_mock, mock):
        service = make_service(db_session, async_mock)
        tickers = [mock(id=1, symbol='USD'), mock(id=2, symbol='EUR')]
        service.repo.get_all_by_symbols.return_value = tickers

        prices = await service.resolve_prices_by_symbol('currency', {'USD': 1.0, 'EUR': 1.1, 'ZWL': 5.0})

        assert prices == {1: 1.0, 2: 1.1}
        service.repo.get_all_by_symbols.assert_awaited_once_with('currency', ['USD', 'EUR', 'ZWL'])

    async def test_missing_symbols_are_skipped(self, db_session, async_mock):
        service = make_service(db_session, async_mock)
        service.repo.get_all_by_symbols.return_value = []

        prices = await service.resolve_prices_by_symbol('currency', {'USD': 1.0, 'EUR': 1.1})

        assert prices == {}

    async def test_empty_prices_skip_query(self, db_session, async_mock):
        service = make_service(db_session, async_mock)

        prices = await service.resolve_prices_by_symbol('currency', {})

        assert prices == {}
        service.repo.get_all_by_symbols.assert_not_awaited()
