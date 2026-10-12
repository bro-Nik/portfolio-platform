from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exporting import fetch_all, model_rows
from app.modules.auth.protocols import ExportAccumulator, UserDataCollector
from app.modules.market.models import Ticker, TickerExternalId, TickerIdentifier


class TickerDataCollector(UserDataCollector):
    """Разделы тикеров, затронутых данными пользователя.

    Читает ticker_ids, собранные коллектором portfolios, — поэтому агрегат
    в app.di вызывает его последним.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def collect(self, user_id: int, acc: ExportAccumulator) -> None:
        ids = acc.ticker_ids
        referenced = await fetch_all(self._session, Ticker, Ticker.id.in_(ids)) if ids else []
        identifiers = (
            await fetch_all(self._session, TickerIdentifier, TickerIdentifier.ticker_id.in_(ids)) if ids else []
        )
        external_ids = (
            await fetch_all(self._session, TickerExternalId, TickerExternalId.ticker_id.in_(ids)) if ids else []
        )
        acc.sections['tickers'] = model_rows(referenced)
        acc.sections['ticker_identifiers'] = model_rows(identifiers)
        acc.sections['ticker_external_ids'] = model_rows(external_ids)
