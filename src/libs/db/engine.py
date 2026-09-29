from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine


def create_engine(
    database_url: str,
    *,
    echo: bool,
    pool_size: int,
    max_overflow: int,
) -> AsyncEngine:
    """Create the service's async engine.

    `pool_size` connections are kept open and reused; under load the pool opens
    up to `max_overflow` more and closes them again when they go idle. So the
    ceiling is pool_size + max_overflow, and a request that finds the pool
    exhausted waits (30s by default) rather than failing immediately.
    """
    return create_async_engine(
        database_url,
        echo=echo,
        pool_pre_ping=True,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)
