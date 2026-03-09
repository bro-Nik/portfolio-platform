from pydantic import model_validator
from pydantic_settings import SettingsConfigDict
from shared.core.config import Settings as CommonSettings


class Settings(CommonSettings):
    db_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_url: str = 'postgresql+asyncpg://postgres:@portfolios-db/postgres'

    env: str = 'development'

    redis_url: str = 'redis://redis:6379/0'
    redis_max_connections: int = 20
    redis_timeout: int = 5

    rate_limit_default: str = '10/minute'
    rate_limit_auth: str = '10/minute'
    rate_limit_public: str = '10/minute'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @model_validator(mode='after')
    def validate_production_settings(self):
        if self.env != 'production':
            return self

        if self.db_url == 'postgresql+asyncpg://postgres:@db/postgres':
            raise ValueError('Нужно определить DB_URL для production!')

        return self

    @property
    def sync_db_url(self) -> str:
        return self.db_url.replace('+asyncpg', '')


settings = Settings()
