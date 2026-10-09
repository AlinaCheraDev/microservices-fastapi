"""Model registry for the pets service.

Every model module MUST be imported here. A table only reaches `Base.metadata`
as a side effect of its module being imported, and Alembic's --autogenerate
reads `Base.metadata` — a model missing from this file produces an empty
migration with no error.
"""

from src.pets.models.pet import Pet

__all__ = ["Pet"]
