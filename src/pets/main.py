from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.libs.db.lifespan import database_lifespan
from src.libs.db.session import get_session
from src.pets.config import PetsSettings, get_settings

app = FastAPI(lifespan=database_lifespan(get_settings))

SettingsDep = Annotated[PetsSettings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]


@app.get("/")
async def read_root(settings: SettingsDep, session: SessionDep):
    # A round-trip to Postgres: proves the URL, credentials and network all work.
    postgres_version = (await session.execute(text("SELECT version()"))).scalar_one()
    return {
        "service": f"pets @ {settings.service_host}:{settings.service_port}",
        "database": f"{settings.postgres_user}@{settings.postgres_db}",
        "postgres": postgres_version,
    }
