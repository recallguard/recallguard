"""Database initialization utilities."""
from __future__ import annotations

from .models import Base
from backend.utils.db import ENGINE


def create_tables() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=ENGINE)


if __name__ == "__main__":  # pragma: no cover - manual invocation
    create_tables()
