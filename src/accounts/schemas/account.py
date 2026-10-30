from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

from src.accounts.schemas.permission import PermissionRead

PASSWORD_MIN_LENGTH = 8
# bcrypt only hashes the first 72 *bytes* and bcrypt>=5 raises on anything longer.
# It's a byte limit, not a character limit: "é" is 2 bytes in UTF-8, so it can't be a max_length.
BCRYPT_MAX_BYTES = 72


def _check_bcrypt_limit(password: str) -> str:
    if len(password.encode()) > BCRYPT_MAX_BYTES:
        #raise ValueError(f"password must be at most {BCRYPT_MAX_BYTES} bytes")
        raise ValueError("password is too long")
    return password


# The email column is unique but case-sensitive, so "Ana@x.com" and "ana@x.com" would be
# two accounts. Lowercasing on the way in keeps one account per address.
Email = Annotated[EmailStr, AfterValidator(str.lower)]
Password = Annotated[str, Field(min_length=PASSWORD_MIN_LENGTH), AfterValidator(_check_bcrypt_limit)]


class AccountCreate(BaseModel):
    """Body of POST /accounts."""

    # Reject unknown fields, so a client sending e.g. "is_deleted" gets a 422 instead of silent ignoring.
    model_config = ConfigDict(extra="forbid")

    email: Email
    # The plain password: the service hashes it and only the hash is stored.
    password: Password
    is_admin: bool = False
    permission_ids: list[UUID] = Field(default_factory=list)


class AccountUpdate(BaseModel):
    """Body of PATCH /accounts/{id}. Every field is optional: only the ones sent are changed.

    The service must read it with `model_dump(exclude_unset=True)`. That tells "not sent"
    (leave alone) apart from an explicit value, which a plain `None` check cannot.
    """

    model_config = ConfigDict(extra="forbid")

    email: Email | None = None
    password: Password | None = None
    is_admin: bool | None = None
    # Replaces the whole list when sent; [] removes every permission.
    permission_ids: list[UUID] | None = None

class AccountRead(BaseModel):
    """An account as returned by the API.

    Deliberately has no password_hash: a response can only ever contain the fields
    declared here, whatever the ORM object holds. is_deleted and deleted_by are left
    out too, since deleted accounts are never returned.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    is_admin: bool
    permissions: list[PermissionRead]
    created_at: datetime
    updated_at: datetime
