"""Database helper."""
import sqlite3
from pathlib import Path


def connect(db_path: Path) -> sqlite3.Connection:
    """Return a connection with row access by name."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

