
"""Database initialization helpers."""

from __future__ import annotations

import sqlite3
from pathlib import Path


def create_tables(conn: sqlite3.Connection) -> None:
    """Create required tables if they do not exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS recalls (
<<<<<<< HEAD
            id INTEGER PRIMARY KEY,
            product TEXT NOT NULL,
            hazard TEXT,
            recall_date TEXT,
            source TEXT
=======
            id TEXT NOT NULL,
            product TEXT NOT NULL,
            hazard TEXT,
            recall_date TEXT,
            source TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            PRIMARY KEY (id, source)
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
        )
        """
    )

<<<<<<< HEAD

=======
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
def init_db(db_path: Path) -> None:
    """Create tables and seed data if the DB is empty."""
    first = not Path(db_path).exists()
    conn = sqlite3.connect(db_path)
<<<<<<< HEAD

    create_tables(conn)
    if first:

    if first:
        schema_path = Path(__file__).with_name("schema.sql")
        conn.executescript(schema_path.read_text())

=======
    create_tables(conn)
    if first:
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
        from . import seed_data

        seed_data.seed(Path(db_path))
    conn.close()

