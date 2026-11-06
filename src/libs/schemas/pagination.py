from pydantic import BaseModel


class Page[T](BaseModel):
    """One page of a list endpoint's results.

    Generic over the item schema, so `Page[AccountRead]` and `Page[PetRead]` each
    get their own, fully typed entry in the OpenAPI docs.
    """

    items: list[T]
    # Count of all matching rows, not just this page, so clients can work out how many pages there are.
    total: int
    limit: int
    offset: int
