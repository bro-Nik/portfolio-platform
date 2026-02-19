from enum import Enum

from pydantic import RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class MarketType(str, Enum):
    CRYPTO = 'crypto'
    STOCK = 'stock'
    CURRENCY = 'currency'


class MarketTickerPrefix(str):
    CRYPTO = 'cr-'
    STOCK = 'st-'
    CURRENCY = 'cu-'


class Settings(BaseSettings):
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_url: str = 'postgresql+asyncpg://postgres:@db/postgres'

    jwt_secret: str = 'super-secret-jwt-token-with-at-least-32-characters-long'
    jwt_algorithm: str = 'HS256'
    env: str = 'development'

    redis_url: str = 'redis://redis:6379/0'
    redis_max_connections: int = 20
    redis_timeout: int = 5

    rate_limit_default: str = '10/minute'
    rate_limit_auth: str = '10/minute'
    rate_limit_public: str = '10/minute'

    model_config = SettingsConfigDict(
        env_file=['.env', '.env.root'],
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
            raise ValueError('Нужно определить DB_URL для production!')

        return self

    @property
    def sync_db_url(self) -> str:
        return self.db_url.replace('+asyncpg', '')


settings = Settings()
