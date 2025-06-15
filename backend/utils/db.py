"""Database helper."""
import sqlite3
from pathlib import Path


def connect(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(db_path)

