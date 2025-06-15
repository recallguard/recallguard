
"""Database initialization helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def init_db(db_path: Path) -> None:
    """Create tables and seed data if the DB is empty."""
    first = not Path(db_path).exists()
    conn = sqlite3.connect(db_path)
    if first:
        schema_path = Path(__file__).with_name("schema.sql")
        conn.executescript(schema_path.read_text())
        from . import seed_data

        seed_data.seed(Path(db_path))
    conn.close()

