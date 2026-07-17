from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    jwt_secret: str = 'super-secret-jwt-token-with-at-least-32-characters-long'
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire_minutes: int = 1
    jwt_refresh_token_expire_days: int = 30

    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_url: str = 'postgresql+asyncpg://postgres:@db/postgres'

    env: str = 'development'

    redis_url: str = 'redis://redis:6379/0'
    redis_max_connections: int = 20
    redis_timeout: int = 5

    rate_limit_default: str = '10/minute'
    rate_limit_auth: str = '10/minute'
    rate_limit_public: str = '10/minute'

    smtp_host: str = ''
    smtp_port: int = 587
    smtp_user: str = ''
    smtp_password: str = ''
    smtp_from_email: str = 'noreply@portfolios.app'

    frontend_url: str = 'http://localhost:3000'
    email_verification_token_expire_hours: int = 48
    password_reset_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @model_validator(mode='after')
    def validate_production_settings(self):
        if self.env != 'production':
            return self

        if self.jwt_secret == 'super-secret-jwt-token-with-at-least-32-characters-long':
            raise ValueError('Нужно определить JWT_SECRET для production!')

        if self.db_url == 'postgresql+asyncpg://postgres:@db/postgres':
            raise ValueError('DB_URL must be set for production!')

        return self

    @property
    def sync_db_url(self) -> str:
        return self.db_url.replace('+asyncpg', '')


settings = Settings()
