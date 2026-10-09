from collections.abc import Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.libs.config import BaseServiceSettings
from src.libs.db.engine import create_engine, create_session_factory


def database_lifespan(get_settings_fn: Callable[[], BaseServiceSettings]):
    """Build a FastAPI lifespan that owns the service's database engine.

    One engine per process: created at startup, disposed at shutdown. The
    session factory is published on `app.state.session_factory`, which is where
    `src.libs.db.session.get_session` looks for it — the two must agree, so they
    live side by side.

    Takes the settings *function* rather than a settings object so that nothing
    reads the environment at import time.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        settings = get_settings_fn()
        engine = create_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=settings.postgres_pool_size,
            max_overflow=settings.postgres_max_overflow,
        )
        app.state.session_factory = create_session_factory(engine)
        try:
            yield
        finally:
            await engine.dispose()

    return lifespan
