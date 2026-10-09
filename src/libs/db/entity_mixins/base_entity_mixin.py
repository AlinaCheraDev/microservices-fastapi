from datetime import datetime

from sqlalchemy import DateTime, func, UUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4, UUID


class BaseEntityMixin:
    id: Mapped[PrimaryKey[UUID]] = mapped_column(primary_key=True, server_default=uuid4())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
