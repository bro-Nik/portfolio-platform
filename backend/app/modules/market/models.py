from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class TickerExternalId(Base):
    __tablename__ = 'ticker_external_id'

    ticker_id: Mapped[int] = mapped_column(Integer, ForeignKey('ticker.id', ondelete='CASCADE'), primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    external_id: Mapped[str] = mapped_column(String(256), nullable=False, index=True)

    ticker: Mapped['Ticker'] = relationship(back_populates='external_ids')


class TickerIdentifier(Base):
    __tablename__ = 'ticker_identifier'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker_id: Mapped[int] = mapped_column(Integer, ForeignKey('ticker.id', ondelete='CASCADE'), nullable=False, index=True)
    system: Mapped[str] = mapped_column(String(64), nullable=False)
    value: Mapped[str] = mapped_column(String(512), nullable=False)

    __table_args__ = (
        UniqueConstraint('system', 'value', name='uq_ticker_identifier_system_value'),
    )

    ticker: Mapped['Ticker'] = relationship(back_populates='identifiers')


class Ticker(Base):
    __tablename__ = 'ticker'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(1024), nullable=False)
    symbol: Mapped[str] = mapped_column(String(124), nullable=False, index=True)
    image: Mapped[str | None] = mapped_column(String(1024))
    market_cap_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price: Mapped[float] = mapped_column(Float, default=0.0)
    price_updated_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    market: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC))

    external_ids: Mapped[list[TickerExternalId]] = relationship(back_populates='ticker', cascade='all, delete-orphan')
    identifiers: Mapped[list[TickerIdentifier]] = relationship(back_populates='ticker', cascade='all, delete-orphan')


class Provider(Base):
    __tablename__ = 'provider'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    api_key: Mapped[str | None] = mapped_column(String(500))
    supported_markets: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)

    requests_per_minute: Mapped[int | None] = mapped_column(Integer)
    requests_per_hour: Mapped[int | None] = mapped_column(Integer)
    requests_per_day: Mapped[int | None] = mapped_column(Integer)
    requests_per_month: Mapped[int | None] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    retry_delay: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    timeout: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    total_requests: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    successful_requests: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    failed_requests: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    avg_response_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class RequestLog(Base):
    __tablename__ = 'request_log'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    provider_name: Mapped[str | None] = mapped_column(String(100), index=True)
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False)
    method: Mapped[str] = mapped_column(String(10), default='GET', nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer)
    response_time: Mapped[float | None] = mapped_column(Float)
    response_size: Mapped[int | None] = mapped_column(Integer)

    was_successful: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    error_type: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str | None] = mapped_column(Text)
    error_details: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    request_url: Mapped[str] = mapped_column(Text, nullable=False)
    request_headers: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    request_params: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    request_body: Mapped[str | None] = mapped_column(Text)

    response_headers: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    response_body_preview: Mapped[str | None] = mapped_column(Text)
    response_content_type: Mapped[str | None] = mapped_column(String(200))

    task_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('task.id', ondelete='CASCADE'), index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now(UTC), nullable=False)

    task: Mapped['Task | None'] = relationship(back_populates='request_logs')


class Task(Base):
    __tablename__ = 'task'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    task_type: Mapped[str] = mapped_column(String(100), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    schedule: Mapped[str] = mapped_column(String(100), nullable=False)
    schedule_type: Mapped[str] = mapped_column(String(20), default='cron', nullable=False)
    timezone: Mapped[str] = mapped_column(String(50), default='UTC', nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    status: Mapped[str | None] = mapped_column(String(200))

    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    task_priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)

    last_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_run_status: Mapped[str | None] = mapped_column(String(50))
    last_run_result: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    last_error: Mapped[str | None] = mapped_column(Text)
    next_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    run_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    success_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    error_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    request_logs: Mapped[list['RequestLog']] = relationship(back_populates='task')
