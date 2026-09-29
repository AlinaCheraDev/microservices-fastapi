from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for the accounts service. Owns this service's MetaData."""
    pass
