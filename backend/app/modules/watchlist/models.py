from datetime import UTC, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.modules.auth.models import User


class WatchlistItem(Base):
    __tablename__ = 'watchlist_item'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    ticker_id: Mapped[int] = mapped_column(Integer, index=True)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (UniqueConstraint('user_id', 'ticker_id', name='uq_watchlist_item_user_ticker'),)

    alerts: Mapped[list['PriceAlert']] = relationship(back_populates='watchlist_item', cascade='all, delete-orphan')
    user: Mapped['User'] = relationship(back_populates='watchlist_items')


class PriceAlert(Base):
    __tablename__ = 'price_alert'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    watchlist_item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('watchlist_item.id', ondelete='CASCADE'),
        index=True,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    target_price_usd: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    currency_symbol: Mapped[str] = mapped_column(String(16), nullable=False, default='USD')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    triggered_price: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    watchlist_item: Mapped['WatchlistItem'] = relationship(back_populates='alerts')
