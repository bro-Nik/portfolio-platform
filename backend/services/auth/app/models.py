from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, ForeignKey, Integer, String
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base

from app.schemas.user import UserRole

Base = declarative_base()


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    expires_at: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Связи
    user: Mapped['User'] = relationship('User', back_populates='refresh_tokens')
    login_session: Mapped[Optional['LoginSession']] = relationship(
        'LoginSession',
        back_populates='refresh_token',
        uselist=False,
        cascade='all, delete-orphan',
    )


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, create_constraint=True, validate_strings=True),
        nullable=False,
        default=UserRole.USER,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
    last_active_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_active_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default='active', nullable=False)

    # Связи
    refresh_tokens: Mapped[list['RefreshToken']] = relationship(
        'RefreshToken',
        back_populates='user',
        cascade='all, delete-orphan',
    )
    login_sessions: Mapped[list['LoginSession']] = relationship(
        'LoginSession',
        back_populates='user',
        cascade='all, delete-orphan',
    )


class LoginSession(Base):
    __tablename__ = 'login_sessions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )
    refresh_token_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('refresh_tokens.id', ondelete='CASCADE'),
        nullable=False,
        unique=True,
    )

    # Информация о подключении
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255))
    device_type: Mapped[Optional[str]] = mapped_column(String(50))  # mobile, desktop, tablet
    browser: Mapped[Optional[str]] = mapped_column(String(100))
    os: Mapped[Optional[str]] = mapped_column(String(100))
    platform: Mapped[Optional[str]] = mapped_column(String(100))  # Windows, iOS, Android, etc.

    # Временные метки
    login_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_activity_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    # Связи
    user: Mapped['User'] = relationship('User', back_populates='login_sessions')
    refresh_token: Mapped['RefreshToken'] = relationship(
        'RefreshToken',
        back_populates='login_session',
    )
