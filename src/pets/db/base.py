from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for the pets service. Owns this service's MetaData."""
    pass
