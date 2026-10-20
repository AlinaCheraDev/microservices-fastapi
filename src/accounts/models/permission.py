from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.accounts.db.base import Base
from src.libs.db.entity_mixins import BaseEntityMixin


class Permission(Base, BaseEntityMixin):
    """Something an account is allowed to do, e.g. "pets:delete"."""

    __tablename__ = "permissions"

    # Unique: permissions are looked up by name when checking access.
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(255))
