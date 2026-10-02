"""Выгрузка персональных данных пользователя.

Право на доступ к своим данным (152-ФЗ, ст. 14). Раньше приложение давало его
только визуально — через интерфейс; машиночитаемой копии у субъекта не было.
"""

from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User
from app.modules.auth.repositories import SessionRepository
from app.modules.market.models import Ticker, TickerExternalId, TickerIdentifier
from app.modules.portfolios.models import (
    Portfolio,
    PortfolioAsset,
    Transaction,
    Wallet,
    WalletAsset,
)
from app.modules.tags.models import Tag, Taggable
from app.modules.watchlist.models import PriceAlert, WatchlistItem

#: Версия формата выгрузки: меняется при добавлении новых разделов.
EXPORT_VERSION = 2

#: Поля, которые не попадают в выгрузку: выгрузка предназначена для предъявления
#: субъекту, а не для переноса сессий или доступа к чужим ресурсам.
SECRET_FIELDS = frozenset(
    {
        'password_hash',
        'token',
        'token_hash',
        'reset_password_token_hash',
        'reset_password_token_expires_at',
    }
)


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return value


def _rows(entities: list[Any]) -> list[dict[str, Any]]:
    """Самоописание строк по колонкам модели, без секретных полей."""
    if not entities:
        return []
    columns = [c for c in entities[0].__table__.columns if c.key not in SECRET_FIELDS]
    return [{c.key: _serialize(getattr(entity, c.key)) for c in columns} for entity in entities]


async def _all(session: AsyncSession, model: Any, *conditions: Any) -> list[Any]:
    stmt = select(model).where(*conditions) if conditions else select(model)
    return list((await session.execute(stmt)).scalars())


async def export_user_data(session: AsyncSession, user_id: int) -> dict[str, Any]:
    """Полная выгрузка данных пользователя в машиночитаемом виде."""
    user = await session.get(User, user_id)
    if not user:
        return {}

    portfolios = await _all(session, Portfolio, Portfolio.user_id == user_id)
    wallets = await _all(session, Wallet, Wallet.user_id == user_id)
    transactions = await _all(session, Transaction, Transaction.user_id == user_id)
    portfolio_assets = await _all(session, PortfolioAsset, PortfolioAsset.user_id == user_id)
    wallet_assets = await _all(session, WalletAsset, WalletAsset.user_id == user_id)
    tags = await _all(session, Tag, Tag.user_id == user_id)
    taggables = await _all(session, Taggable, Taggable.tag_id.in_([t.id for t in tags])) if tags else []
    watchlist_items = await _all(session, WatchlistItem, WatchlistItem.user_id == user_id)
    price_alerts = await _all(session, PriceAlert, PriceAlert.user_id == user_id)

    ticker_ids = {
        *[a.ticker_id for a in portfolio_assets],
        *[a.ticker_id for a in wallet_assets],
        *[t.ticker_id for t in transactions if t.ticker_id],
        *[t.ticker2_id for t in transactions if t.ticker2_id],
    }
    referenced = await _all(session, Ticker, Ticker.id.in_(ticker_ids)) if ticker_ids else []
    identifiers = (
        await _all(session, TickerIdentifier, TickerIdentifier.ticker_id.in_(ticker_ids)) if ticker_ids else []
    )
    external_ids = (
        await _all(session, TickerExternalId, TickerExternalId.ticker_id.in_(ticker_ids)) if ticker_ids else []
    )

    return {
        'export_version': EXPORT_VERSION,
        'exported_at': datetime.now(UTC).isoformat(),
        'user': _rows([user]),
        'sessions': _rows(await SessionRepository(session).get_all_by_user_id(user_id)),
        'portfolios': _rows(portfolios),
        'portfolio_assets': _rows(portfolio_assets),
        'wallets': _rows(wallets),
        'wallet_assets': _rows(wallet_assets),
        'transactions': _rows(transactions),
        'tags': _rows(tags),
        'taggable': _rows(taggables),
        'watchlist_items': _rows(watchlist_items),
        'price_alerts': _rows(price_alerts),
        'tickers': _rows(referenced),
        'ticker_identifiers': _rows(identifiers),
        'ticker_external_ids': _rows(external_ids),
    }
