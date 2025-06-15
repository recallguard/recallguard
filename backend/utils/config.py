"""Configuration utilities."""
from __future__ import annotations

import os


def get_database_url() -> str:
    """Return the SQLAlchemy connection string."""
    return os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///dev.db")

