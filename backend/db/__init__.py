"""Database initialization helpers."""

from __future__ import annotations

from backend.utils.session import get_engine
from sqlalchemy import text
from .models import metadata
from .seed_data import seed
import sqlite3
from pathlib import Path


def init_db() -> None:
    """Create tables if they do not exist."""
    metadata.create_all(bind=get_engine())
    with get_engine().connect() as conn:
        if not conn.execute(text('SELECT COUNT(*) FROM users')).fetchone()[0]:
            seed()


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
            id TEXT NOT NULL,
            product TEXT NOT NULL,
            hazard TEXT,
            recall_date TEXT,
            source TEXT NOT NULL,
            fetched_at TEXT NOT NULL,
            PRIMARY KEY (id, source)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS user_items (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            upc TEXT NOT NULL,
            label TEXT,
            profile TEXT NOT NULL DEFAULT 'self',
            added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )


def init_db_path(db_path: Path) -> None:
    """Create tables and seed data if the DB is empty."""
    first = not Path(db_path).exists()
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    if first:
        from . import seed_data

        seed_data.seed_path(Path(db_path))
    conn.close()


