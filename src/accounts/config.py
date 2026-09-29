from functools import lru_cache

from pydantic import Field

from src.libs.config import BaseServiceSettings


class AccountsSettings(BaseServiceSettings):
    """Configuration for the accounts service.

    The shared fields (`postgres_host`, `postgres_port`, ...) and the `.env`
    location are inherited. Everything below is owned by this service, so it is
    mapped explicitly with `validation_alias` to the ACCOUNTS_* variables.
    """

    # Owned by this service
    postgres_user: str = Field(validation_alias="ACCOUNTS_POSTGRES_USER")
    postgres_password: str = Field(validation_alias="ACCOUNTS_POSTGRES_PASSWORD")
    postgres_db: str = Field(validation_alias="ACCOUNTS_POSTGRES_DB")

    postgres_pool_size: int = Field(validation_alias="ACCOUNTS_POSTGRES_POOL_SIZE")
    postgres_max_overflow: int = Field(validation_alias="ACCOUNTS_POSTGRES_MAX_OVERFLOW")

    redis_url: str = Field(validation_alias="ACCOUNTS_REDIS_URL")
    jwt_secret: str = Field(validation_alias="ACCOUNTS_JWT_SECRET")

    service_host: str = Field(validation_alias="ACCOUNTS_SERVICE_HOST")
    service_port: int = Field(validation_alias="ACCOUNTS_SERVICE_PORT")


@lru_cache
def get_settings() -> AccountsSettings:
    """Return the singleton settings instance.

    Cached so the .env file is parsed once per process, and so tests can override
    the values by calling `get_settings.cache_clear()`.
    """
    return AccountsSettings()
