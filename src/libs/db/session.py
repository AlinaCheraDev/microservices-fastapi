from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield one AsyncSession per request, then close it.

    A generator dependency: FastAPI runs everything above the `yield` before the
    endpoint, hands the session in, then resumes below it once the response is
    sent. That is what makes the cleanup automatic — the `async with` block exits
    however the endpoint ended.

    Per request, not per application: a session is not just a connection, it also
    owns an identity map and an open transaction, so two requests sharing one
    would see each other's uncommitted rows and roll each other back. Within a
    single request the opposite holds — FastAPI caches the dependency, so an
    endpoint taking both a session and a service that depends on this same
    function gets one session, and therefore one transaction, for the whole
    request.

    Closing returns the connection to the pool, so a session holds a pool slot for
    as long as it is open: at most `pool_size + max_overflow` requests can be
    inside this function at once, and the next one waits (30s by default) before
    raising. The fix for that is to not hold a session across a slow call, not to
    share sessions between requests.

    Expects the service's lifespan to have put an `async_sessionmaker` on
    `app.state.session_factory`. The factory is read at request time rather than
    captured at import time, because the engine does not exist until startup.

    Rolls back on error; committing is the service layer's job, since only it
    knows where a business operation ends.
    """
    session_factory = request.app.state.session_factory
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
