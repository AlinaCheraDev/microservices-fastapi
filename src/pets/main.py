from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.libs.db.lifespan import database_lifespan
from src.libs.db.session import get_session
from src.pets.config import get_settings

app = FastAPI(lifespan=database_lifespan(get_settings))

SessionDep = Annotated[AsyncSession, Depends(get_session)]

# TODO: Decide which one is relevant for k8s to use for liveliness probe


@app.get("/health/live")
async def live():
    return {"status": "ok"}  # process is running, nothing else


@app.get("/health/ready")
async def ready(session: SessionDep):
    await session.execute(text("SELECT 1"))  # can reach its DB (and Redis, later)
    return {"status": "ok"}
