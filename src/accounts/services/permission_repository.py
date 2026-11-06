from collections.abc import Iterable
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.accounts.models import Permission


class PermissionRepository:
    """Database access for permissions. Never commits, like AccountRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_many(self, permission_ids: Iterable[UUID]) -> list[Permission]:
        """Return the permissions with these ids, skipping any id that does not exist.

        Missing ids are not an error here: the service compares what came back with
        what was asked for and decides how to report the difference.
        """
        ids = set(permission_ids)
        if not ids:
            return []
        stmt = select(Permission).where(Permission.id.in_(ids))
        return list(await self.session.scalars(stmt))
