import asyncio

import bcrypt


async def hash_password(password: str) -> str:
    """Return the bcrypt hash of `password`, a 60-character string.

    bcrypt is slow on purpose (a few hundred ms) to make guessing passwords
    expensive. Called directly it would block the event loop, and every other
    request in this process would wait. `to_thread` runs it in a worker thread,
    so the loop keeps serving other requests in the meantime.

    The schemas already reject passwords over bcrypt's 72-byte limit.
    """
    hashed = await asyncio.to_thread(bcrypt.hashpw, password.encode(), bcrypt.gensalt())
    return hashed.decode()
