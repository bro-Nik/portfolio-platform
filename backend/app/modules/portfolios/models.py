from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Portfolio(Base):
    __tablename__ = 'portfolio'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    market: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str | None] = mapped_column(String(1024))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    assets: Mapped[list['PortfolioAsset']] = relationship(back_populates='portfolio', cascade='all, delete-orphan')
    user: Mapped['User'] = relationship(back_populates='portfolios')


class PortfolioAsset(Base):
    __tablename__ = 'portfolio_asset'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    ticker_id: Mapped[int] = mapped_column(Integer)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey('portfolio.id', ondelete='CASCADE'))
    quantity: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    buy_orders: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    sell_orders: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    amount: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    realized_profit: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    total_invested: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    percent: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    comment: Mapped[str | None] = mapped_column(String(1024))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    portfolio: Mapped['Portfolio'] = relationship(back_populates='assets')


class Transaction(Base):
    __tablename__ = 'transaction'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))
    ticker_id: Mapped[int] = mapped_column(Integer)
    ticker2_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric)
    quantity2: Mapped[Decimal | None] = mapped_column(Numeric)
    price: Mapped[Decimal | None] = mapped_column(Numeric)
    price_usd: Mapped[Decimal | None] = mapped_column(Numeric)
    type: Mapped[str] = mapped_column(String(24))
    comment: Mapped[str | None] = mapped_column(String(1024))
    wallet_id: Mapped[int | None] = mapped_column(ForeignKey('wallet.id'))
    wallet2_id: Mapped[int | None] = mapped_column(ForeignKey('wallet.id'))
    portfolio_id: Mapped[int | None] = mapped_column(ForeignKey('portfolio.id'))
    portfolio2_id: Mapped[int | None] = mapped_column(ForeignKey('portfolio.id'))
    order: Mapped[bool | None] = mapped_column(Boolean)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    def get_direction(self, cancel: bool = False) -> int:
        positive_types = {'Buy', 'Input', 'TransferIn', 'Earning'}
        direction = 1 if self.type in positive_types else -1
        return direction * -1 if cancel else direction


class Wallet(Base):
    __tablename__ = 'wallet'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    comment: Mapped[str | None] = mapped_column(String(1024))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    assets: Mapped[list['WalletAsset']] = relationship(back_populates='wallet', cascade='all, delete-orphan')
    user: Mapped['User'] = relationship(back_populates='wallets')


class Tag(Base):
    __tablename__ = 'tag'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    color: Mapped[str | None] = mapped_column(String(7))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)

    user: Mapped['User'] = relationship(back_populates='tags')


class Taggable(Base):
    __tablename__ = 'taggable'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey('tag.id', ondelete='CASCADE'))
    entity_type: Mapped[str] = mapped_column(String(32))
    entity_id: Mapped[int] = mapped_column(Integer)


class WalletAsset(Base):
    __tablename__ = 'wallet_asset'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker_id: Mapped[int] = mapped_column(Integer)
    wallet_id: Mapped[int] = mapped_column(ForeignKey('wallet.id', ondelete='CASCADE'))
    quantity: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    buy_orders: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    sell_orders: Mapped[Decimal] = mapped_column(Numeric, default=Decimal(0))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False)

    wallet: Mapped['Wallet'] = relationship(back_populates='assets')
