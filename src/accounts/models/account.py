from uuid import UUID

from sqlalchemy import Column, ForeignKey, String, Table, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.accounts.db.base import Base
from src.accounts.models.permission import Permission
from src.libs.db.entity_mixins import BaseEntityMixin

# Many-to-many link between accounts and permissions. A plain Table rather than a
# model class: it has no columns of its own beyond the two keys, so nothing ever
# needs to load it as an object. Deleting either side removes the link rows.
account_permissions = Table(
    "account_permissions",
    Base.metadata,
    Column("account_id", ForeignKey("accounts.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Account(Base, BaseEntityMixin):
    """A user of the system, identified by email."""

    __tablename__ = "accounts"

    # Unique also gives us the index used by login lookups.
    email: Mapped[str] = mapped_column(String(255), unique=True)
    # Never the plain password: a bcrypt hash is always 60 characters.
    password_hash: Mapped[str] = mapped_column(String(60))
    is_admin: Mapped[bool] = mapped_column(default=False, server_default=false())
    # Soft delete: the row stays, queries filter it out.
    is_deleted: Mapped[bool] = mapped_column(default=False, server_default=false())
    # The admin who deleted it. Same database, so unlike Pet.owner_id this can be a real ForeignKey.
    deleted_by: Mapped[UUID | None] = mapped_column(ForeignKey("accounts.id"))

    # selectin: loaded with a second SELECT ... WHERE account_id IN (...) right after the
    # accounts. An AsyncSession cannot lazy-load on attribute access, so the default
    # lazy="select" would raise MissingGreenlet the first time `account.permissions` is read.
    permissions: Mapped[list[Permission]] = relationship(secondary=account_permissions, lazy="selectin")
