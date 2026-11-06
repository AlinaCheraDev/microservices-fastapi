from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.models import Account

# Soft delete: a deleted account keeps its row, so every read for the API must filter it out.
_NOT_DELETED = Account.is_deleted.is_(False)


class AccountRepository:
    """Database access for accounts. The only place that builds account queries.

    Never commits: it works inside the session's transaction and leaves ending it
    to the service layer, which knows where a business operation ends.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, account_id: UUID) -> Account | None:
        """Return the account with this id, or None if there is none or it was deleted."""
        stmt = select(Account).where(Account.id == account_id, _NOT_DELETED)
        return await self.session.scalar(stmt)

    async def get_by_email(self, email: str) -> Account | None:
        """Return the active account with this email, or None. Used by login."""
        stmt = select(Account).where(Account.email == email, _NOT_DELETED)
        return await self.session.scalar(stmt)

    async def email_exists(self, email: str) -> bool:
        """Whether any account, deleted ones included, already uses this email.

        Deleted rows count because the unique constraint on `email` covers them too:
        reusing a deleted account's email would fail on INSERT with an IntegrityError.
        """
        stmt = select(select(Account.id).where(Account.email == email).exists())
        return bool(await self.session.scalar(stmt))

    async def get_page(self, offset: int, limit: int) -> list[Account]:
        """Return one page of active accounts, oldest first.

        `id` breaks ties between equal `created_at` values, so the order is stable
        and no account shows up on two pages or on none.
        """
        stmt = select(Account).where(_NOT_DELETED).order_by(Account.created_at, Account.id).offset(offset).limit(limit)
        return list(await self.session.scalars(stmt))

    async def count(self) -> int:
        """Return how many active accounts there are, for `Page.total`."""
        stmt = select(func.count()).select_from(Account).where(_NOT_DELETED)
        return await self.session.scalar(stmt) or 0

    def add(self, account: Account) -> None:
        """Stage a new account. It is INSERTed at the next flush or commit."""
        self.session.add(account)
