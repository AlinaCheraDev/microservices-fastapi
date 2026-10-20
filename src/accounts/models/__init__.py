"""Model registry for the accounts service.

Every model module MUST be imported here. A table only reaches `Base.metadata`
as a side effect of its module being imported, and Alembic's --autogenerate
reads `Base.metadata` — a model missing from this file produces an empty
migration with no error.
"""

from src.accounts.models.account import Account, account_permissions
from src.accounts.models.permission import Permission

__all__ = ["Account", "Permission", "account_permissions"]
