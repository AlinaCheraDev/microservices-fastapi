from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PermissionRead(BaseModel):
    """A permission as returned by the API."""

    # Lets FastAPI build this straight from a Permission ORM object (it reads attributes, not dict keys).
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime
