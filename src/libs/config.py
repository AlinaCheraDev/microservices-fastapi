from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

# The shared .env lives at the repository root: src/libs/config.py -> src/libs -> src -> <root>
ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"


class BaseServiceSettings(BaseSettings):
    """Settings shared by every service, loaded from the environment / .env file.

    Do not instantiate directly: each service subclasses this and re-declares the
    per-service fields with the `validation_alias` that points at its own
    variables (PETS_POSTGRES_USER, AUTH_POSTGRES_USER, ...). Without that alias a
    field falls back to its own name, which for the credentials below would mean
    connecting as the POSTGRES_USER superuser.
    """

    model_config = SettingsConfigDict(
        env_file=ROOT_ENV,
        env_file_encoding="utf-8",
        extra="ignore",  # the shared .env also holds the other services' variables
    )

    environment: Literal["development", "staging", "production"]
    debug: bool

    # Shared across all services: read from POSTGRES_HOST, POSTGRES_PORT, ...
    postgres_drivername: str
    postgres_host: str
    postgres_port: int

    # Owned by each service: subclasses must re-declare these with their own alias.
    postgres_user: str
    postgres_password: str
    postgres_db: str

    # Pool ceiling is pool_size + max_overflow, per engine, per process. Owned by
    # each service because they scale differently, but they share one server:
    # max_connections is server-wide, so every service's ceiling, times its worker
    # count, has to fit inside the same budget.
    postgres_pool_size: int
    postgres_max_overflow: int

    @property
    def database_url(self) -> str:
        """Connection string for SQLAlchemy and Alembic."""
        return URL.create(
            drivername=self.postgres_drivername,
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        ).render_as_string(hide_password=False)
