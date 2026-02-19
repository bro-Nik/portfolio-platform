from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class Ticker(Base):
    """Тикеры (криптовалюты, акции, валюты)."""

    __tablename__ = 'ticker'

    id: Mapped[str] = mapped_column(String(256), primary_key=True, comment='Уникальный идентификатор')
    name: Mapped[str] = mapped_column(String(1024), nullable=False, comment='Название тикера')
    symbol: Mapped[str] = mapped_column(String(124), nullable=False, index=True, comment='Символ тикера')
    image: Mapped[str | None] = mapped_column(String(1024), comment='URL изображения')
    market_cap_rank: Mapped[int | None] = mapped_column(Integer, nullable=True, comment='Ранг по капитализации')
    price: Mapped[float] = mapped_column(Float, default=0.0, comment='Текущая цена')
    market: Mapped[str] = mapped_column(String(32), nullable=False, index=True, comment='Рынок')
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), comment='Время последнего обновления')

    __table_args__ = (
        Index('idx_ticker_symbol_market', 'symbol', 'market'),
    )


class ApiProvider(Base):
    """Внешние API провайдеры."""

    __tablename__ = 'api_providers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True, comment='Название сервиса')
    display_name: Mapped[str | None] = mapped_column(String(200), comment='Отображаемое имя')
    description: Mapped[str | None] = mapped_column(Text, comment='Описание сервиса')
    api_key: Mapped[str | None] = mapped_column(String(500), comment='API ключ')
    api_key_encrypted: Mapped[bool] = mapped_column(Boolean, default=False, comment='Зашифрован ли ключ')

    # Лимиты запросов
    requests_per_minute: Mapped[int | None] = mapped_column(Integer, comment='Лимит запросов в минуту')
    requests_per_hour: Mapped[int | None] = mapped_column(Integer, comment='Лимит запросов в час')
    requests_per_day: Mapped[int | None] = mapped_column(Integer, comment='Лимит запросов в день')
    requests_per_month: Mapped[int | None] = mapped_column(Integer, comment='Лимит запросов в месяц')

    # Текущие счетчики
    minute_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='Счетчик за минуту')
    hour_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='Счетчик за час')
    day_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='Счетчик за день')
    month_counter: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment='Счетчик за месяц')

    # Время сброса счетчиков
    last_minute_reset: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, comment='Время сброса минутного счетчика')
    last_hour_reset: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, comment='Время сброса часового счетчика')
    last_day_reset: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(UTC).replace(tzinfo=None), comment='Время сброса дневного счетчика')
    last_month_reset: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, comment='Время сброса месячного счетчика')

    # Настройки
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True, comment='Активен ли сервис')
    retry_delay: Mapped[int] = mapped_column(Integer, default=60, nullable=False, comment='Задержка повтора (сек)')
    timeout: Mapped[int] = mapped_column(Integer, default=30, nullable=False, comment='Таймаут запроса (сек)')
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False, comment='Максимальное количество попыток')
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False, comment='Приоритет сервиса (0-10)')

    # Метрики
    total_requests: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, comment='Общее количество запросов')
    successful_requests: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, comment='Успешные запросы')
    failed_requests: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, comment='Неудачные запросы')
    avg_response_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, comment='Среднее время ответа (мс)')

    # Системные поля
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, comment='Дата создания')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, onupdate=lambda: datetime.now(UTC).replace(tzinfo=None), comment='Дата обновления')

    # Связи
    request_logs: Mapped[list['ApiRequestLog']] = relationship(back_populates='api_provider', cascade='all, delete-orphan')
    tasks: Mapped[list['ApiTask']] = relationship(back_populates='api_provider', cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_api_services_status', 'is_active', 'priority'),
        Index('idx_api_services_usage', 'minute_counter', 'hour_counter', 'day_counter'),
        {'comment': 'Внешние API сервисы с rate limiting'},
    )


class ApiRequestLog(Base):
    """Лог запросов к API."""

    __tablename__ = 'api_request_logs'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # service_id: Mapped[int] = mapped_column(Integer, ForeignKey('api_services.id', ondelete='CASCADE'), nullable=False, index=True, comment="ID сервиса")
    api_provider_id: Mapped[int | None] = mapped_column(Integer, comment='ID сервиса')
    api_provider_name: Mapped[int] = mapped_column(String(100), ForeignKey('api_providers.name', ondelete='CASCADE'), nullable=False, index=True, comment='Название сервиса')
    endpoint: Mapped[str] = mapped_column(String(500), nullable=False, comment='Endpoint API')
    method: Mapped[str] = mapped_column(String(10), default='GET', nullable=False, comment='HTTP метод')
    status_code: Mapped[int | None] = mapped_column(Integer, comment='HTTP статус код')
    response_time: Mapped[float | None] = mapped_column(Float, comment='Время ответа в секундах')
    response_size: Mapped[int | None] = mapped_column(Integer, comment='Размер ответа в байтах')

    # Статус запроса
    was_successful: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment='Успешен ли запрос')
    error_type: Mapped[str | None] = mapped_column(String(100), comment='Тип ошибки')
    error_message: Mapped[str | None] = mapped_column(Text, comment='Сообщение об ошибке')
    error_details: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment='Детали ошибки')

    # Данные запроса
    request_url: Mapped[str] = mapped_column(Text, nullable=False, comment='Полный URL запроса')
    request_headers: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment='Заголовки запроса')
    request_params: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment='Параметры запроса')
    request_body: Mapped[str | None] = mapped_column(Text, comment='Тело запроса')

    # Данные ответа
    response_headers: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment='Заголовки ответа')
    response_body_preview: Mapped[str | None] = mapped_column(Text, comment='Препью тела ответа')
    response_content_type: Mapped[str | None] = mapped_column(String(200), comment='Content-Type ответа')

    # Связь с задачами
    celery_task_id: Mapped[str | None] = mapped_column(String(100), index=True, comment='ID задачи Celery')
    api_task_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('api_tasks.id', ondelete='SET NULL'), index=True, comment='ID запланированной задачи')

    # Системные поля
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, comment='Дата создания')

    # Связи
    api_provider: Mapped['ApiProvider'] = relationship(back_populates='request_logs')
    api_task: Mapped[Optional['ApiTask']] = relationship(back_populates='request_logs')

    __table_args__ = (
        Index('idx_request_logs_service_time', 'api_provider_id', 'created_at'),
        Index('idx_request_logs_success', 'was_successful', 'created_at'),
        {'comment': 'Логи запросов к внешним API'},
    )


class ApiTask(Base):
    """Настроенные задачи."""

    __tablename__ = 'api_tasks'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True, comment='Название задачи')
    description: Mapped[str | None] = mapped_column(Text, comment='Описание задачи')

    # Тип и настройки задачи
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment='Тип задачи')
    api_provider_id: Mapped[int] = mapped_column(Integer, ForeignKey('api_providers.id', ondelete='SET NULL'), nullable=False, index=True, comment='Используемый API сервис')

    # Расписание
    schedule: Mapped[str] = mapped_column(String(100), nullable=False, comment='Cron выражение или интервал')
    schedule_type: Mapped[str] = mapped_column(String(20), default='cron', nullable=False, comment='Тип расписания')
    timezone: Mapped[str] = mapped_column(String(50), default='UTC', nullable=False, comment='Часовой пояс')

    # Статус
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True, comment='Активна ли задача')
    status: Mapped[str | None] = mapped_column(String(200), comment='Статус задачи')

    # Параметры задачи
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False, comment='Параметры задачи')
    task_priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False, comment='Приоритет задачи (0-10)')

    # История выполнения
    last_run: Mapped[datetime | None] = mapped_column(DateTime, comment='Время последнего запуска')
    last_run_status: Mapped[str | None] = mapped_column(String(50), comment='Статус последнего запуска')
    last_run_result: Mapped[dict[str, Any] | None] = mapped_column(JSON, comment='Результат последнего запуска')
    last_error: Mapped[str | None] = mapped_column(Text, comment='Последняя ошибка')
    next_run: Mapped[datetime | None] = mapped_column(DateTime, index=True, comment='Время следующего запуска')

    # TODO
    run_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, comment='Всего запусков')
    success_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, comment='Всего запусков')
    error_count: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, comment='Всего запусков')

    # Системные поля

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, comment='Дата создания')
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None), nullable=False, onupdate=lambda: datetime.now(UTC).replace(tzinfo=None), comment='Дата обновления')
    created_by: Mapped[str | None] = mapped_column(String(100), comment='Создатель')
    updated_by: Mapped[str | None] = mapped_column(String(100), comment='Кто обновил')

    # Связи
    api_provider: Mapped[Optional['ApiProvider']] = relationship(back_populates='tasks')
    request_logs: Mapped[list['ApiRequestLog']] = relationship(back_populates='api_task')

    __table_args__ = (
        Index('idx_scheduled_tasks_active', 'is_active', 'next_run'),
        Index('idx_scheduled_tasks_service', 'api_provider_id', 'is_active'),
        {'comment': 'Периодические задачи для сбора данных'},
    )
