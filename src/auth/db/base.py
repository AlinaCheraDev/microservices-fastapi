from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for the auth service. Owns this service's MetaData."""
    pass
