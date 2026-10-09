from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.libs.db.base import TimestampMixin
from src.pets.db.base import Base


class Pet(Base, TimestampMixin):
    """A pet owned by an account."""

    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    species: Mapped[str] = mapped_column(String(50))
    # The owner lives in the accounts service, so this is a plain id, not a ForeignKey.
    owner_id: Mapped[int | None]
