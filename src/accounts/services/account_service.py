from collections.abc import Iterable
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.models import Account, Permission
from src.accounts.schemas import AccountCreate, AccountRead, AccountUpdate
from src.accounts.services.account_repository import AccountRepository
from src.accounts.services.passwords import hash_password
from src.accounts.services.permission_repository import PermissionRepository
from src.libs.errors import ConflictError, ForbiddenError, InvalidInputError, NotFoundError
from src.libs.schemas.pagination import Page

_EMAIL_TAKEN = "email is already in use"


class AccountService:
    """Business logic for the Admin API: create, read, update and delete accounts.

    The repositories only run queries; this class decides what is allowed and ends
    each operation with a commit. Every method that changes data is one transaction:
    it either commits completely or, if it raises, leaves the database untouched.

    Doesn't check *who* is calling. Making sure only admins reach these methods is
    the job of the endpoint (a `require_admin` dependency, once auth exists). The
    caller's id is passed in only where a rule depends on it.
    """

    def __init__(
        self,
        session: AsyncSession,
        accounts: AccountRepository,
        permissions: PermissionRepository,
    ) -> None:
        self.session = session
        self.accounts = accounts
        self.permissions = permissions

    async def get(self, account_id: UUID) -> Account:
        """Return the account, or raise NotFoundError if it doesn't exist or was deleted."""
        account = await self.accounts.get(account_id)
        if account is None:
            raise NotFoundError(f"account {account_id} not found")
        return account

    async def get_page(self, offset: int, limit: int) -> Page[AccountRead]:
        """Return one page of active accounts. The endpoint validates offset and limit."""
        items = await self.accounts.get_page(offset, limit)
        total = await self.accounts.count()
        return Page[AccountRead](
            items=[AccountRead.model_validate(a) for a in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    async def create(self, data: AccountCreate) -> Account:
        """Create an account. Raises ConflictError if the email is taken, InvalidInputError for unknown permissions."""
        if await self.accounts.email_exists(data.email):
            raise ConflictError(_EMAIL_TAKEN)

        account = Account(
            email=data.email,
            password_hash=await hash_password(data.password),
            is_admin=data.is_admin,
            permissions=await self._load_permissions(data.permission_ids),
        )
        self.accounts.add(account)
        await self._commit(account)
        return account

    async def update(self, account_id: UUID, data: AccountUpdate, *, by: UUID) -> Account:
        """Change only the fields the client sent. `by` is the admin making the change.

        Raises NotFoundError, ConflictError (email taken), InvalidInputError (unknown
        permission, or null for a field that can't be empty) or ForbiddenError (an
        admin removing their own admin rights).
        """
        account = await self.get(account_id)
        # Only the fields present in the request body, with the values sent.
        changes = data.model_dump(exclude_unset=True)

        # The schema accepts null for every field, so "not sent" and "sent as null" can be
        # told apart. None of these columns can be empty, though, so null is refused here.
        nulls = sorted(field for field, value in changes.items() if value is None)
        if nulls:
            raise InvalidInputError(f"cannot be null: {', '.join(nulls)}")

        # Without this an admin could lock themselves out, and the last admin could leave
        # nobody able to manage accounts.
        if account_id == by and changes.get("is_admin") is False:
            raise ForbiddenError("you cannot remove your own admin rights")

        if "email" in changes and changes["email"] != account.email:
            if await self.accounts.email_exists(changes["email"]):
                raise ConflictError(_EMAIL_TAKEN)
            account.email = changes["email"]
        if "password" in changes:
            account.password_hash = await hash_password(changes["password"])
        if "is_admin" in changes:
            account.is_admin = changes["is_admin"]
        if "permission_ids" in changes:
            # Replaces the whole list; SQLAlchemy rewrites the account_permissions rows.
            account.permissions = await self._load_permissions(changes["permission_ids"])

        # No repository call needed: the session tracks changes to objects it loaded,
        # and the commit sends the UPDATE.
        await self._commit(account)
        return account

    async def delete(self, account_id: UUID, *, by: UUID) -> None:
        """Soft-delete the account. `by` is the admin deleting it.

        The row stays (with is_deleted and deleted_by set), so the email stays taken.
        Raises NotFoundError, or ForbiddenError for an admin deleting their own account.
        """
        if account_id == by:
            raise ForbiddenError("you cannot delete your own account")
        account = await self.get(account_id)
        account.is_deleted = True
        account.deleted_by = by
        await self._commit()

    async def _load_permissions(self, permission_ids: Iterable[UUID]) -> list[Permission]:
        """Turn ids into Permission objects. Raises InvalidInputError naming any that don't exist."""
        ids = set(permission_ids)
        found = await self.permissions.get_many(ids)
        missing = ids - {p.id for p in found}
        if missing:
            raise InvalidInputError(f"unknown permission ids: {', '.join(sorted(map(str, missing)))}")
        return found

    async def _commit(self, account: Account | None = None) -> None:
        """Commit, then reload what the database filled in on `account`, if given.

        IntegrityError: the email_exists check and the INSERT/UPDATE are separate
        statements, so two requests can both pass the check with the same email. The
        unique constraint stops the second one; this turns that into the same
        ConflictError the check would have raised. Email is the only unique column a
        request can set, so it's the only constraint that can fail here.

        refresh: created_at and updated_at are set by the database, and SQLAlchemy
        doesn't know their values after a commit. Reading one would make it load them
        from the database on attribute access, which raises MissingGreenlet with an
        AsyncSession. refresh() loads them now, while we can await.
        """
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError(_EMAIL_TAKEN) from None
        if account is not None:
            await self.session.refresh(account)
