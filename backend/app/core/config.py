from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]


JWT_SECRET_DEFAULT = 'super-secret-jwt-token-with-at-least-32-characters-long'


class Settings(BaseSettings):
    jwt_secret: str = JWT_SECRET_DEFAULT
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 30

    db_echo: bool = False
    # Бюджет соединений на процесс: (pool_size + max_overflow).
    # Суммируется по всем процессам (web + воркер + планировщик) и должен
    # помещаться в max_connections PostgreSQL вместе с резервом.
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 10
    db_statement_timeout_ms: int = 30_000
    db_url: str = 'postgresql+asyncpg://postgres:@db/postgres'

    env: str = 'development'

    redis_url: str = 'redis://redis:6379/0'
    redis_max_connections: int = 20
    redis_timeout: int = 5

    rate_limit_default: str = '10/minute'
    rate_limit_auth: str = '10/minute'
    rate_limit_public: str = '10/minute'
    rate_limit_enabled: bool | None = None

    smtp_host: str = ''
    smtp_port: int = 587
    smtp_user: str = ''
    smtp_password: str = ''
    smtp_from_email: str = 'noreply@portfolios.app'

    frontend_url: str = 'http://localhost:3000'
    email_verification_token_expire_hours: int = 48
    password_reset_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / '.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @model_validator(mode='after')
    def validate_production_settings(self) -> Self:
        if self.rate_limit_enabled is None:
            self.rate_limit_enabled = self.env == 'production'

        if self.env != 'production':
            return self

        # В production лимит включён принудительно: явный false из env не должен
        # отключать защиту от перебора паролей на документированных развёртываниях.
        self.rate_limit_enabled = True

        if self.is_insecure_jwt_secret:
            raise ValueError('JWT_SECRET для production должен быть задан явно и быть случайным!')

        return self

    @property
    def is_insecure_jwt_secret(self) -> bool:
        """Секрет совпадает с дефолтом или с примером из репозитория."""
        if self.jwt_secret == JWT_SECRET_DEFAULT:
            return True
        lowered = self.jwt_secret.lower()
        return any(marker in lowered for marker in ('change', 'your-', 'example', 'placeholder', 'secret-token'))

    @property
    def smtp_enabled(self) -> bool:
        return self.smtp_host not in ('', 'mailpit', 'localhost')

    @property
    def sync_db_url(self) -> str:
        # Драйвер указан явно: без этого SQLAlchemy 2.1 выбирает psycopg3,
        # которого в requirements нет, и alembic падает на create_engine.
        return self.db_url.replace('+asyncpg', '+psycopg2')

    @property
    def is_prod(self) -> bool:
        return self.env == 'production'


settings = Settings()
