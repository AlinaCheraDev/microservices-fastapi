"""Request and response shapes (DTOs) for the accounts API.

Kept apart from `models/`: models describe the database tables, schemas describe what
crosses the API boundary. They overlap but are not the same, e.g. AccountCreate takes a
plain password, the Account model stores only its hash, and AccountRead exposes neither.
"""

from src.accounts.schemas.account import AccountCreate, AccountRead, AccountUpdate
from src.accounts.schemas.permission import PermissionRead

__all__ = ["AccountCreate", "AccountRead", "AccountUpdate", "PermissionRead"]
