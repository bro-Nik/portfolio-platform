from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Общие настройки проекта"""

    jwt_secret: str = 'super-secret-jwt-token-with-at-least-32-characters-long'
    jwt_algorithm: str = 'HS256'
    jwt_access_token_expire_minutes: int = 1
    jwt_refresh_token_expire_days: int = 30
    env: str = 'development'
    
    model_config = SettingsConfigDict(
        env_file = "../../.env",
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @model_validator(mode='after')
    def validate_production_settings(self):
        if self.env != 'production':
            return self

        if self.jwt_secret == 'super-secret-jwt-token-with-at-least-32-characters-long':
            raise ValueError('Нужно определить JWT_SECRET для production!')

        return self


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
