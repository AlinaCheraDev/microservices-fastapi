from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.libs.db.entity_mixins import BaseEntityMixin
from src.pets.db.base import Base
from uuid import UUID


class Pet(Base, BaseEntityMixin):
    """A pet owned by an account."""

    __tablename__ = "pets"

    name: Mapped[str] = mapped_column(String(100))
    species: Mapped[str] = mapped_column(String(50))
    # The owner lives in the accounts service, so this is a plain id, not a ForeignKey.
    owner_id: Mapped[UUID | None]
