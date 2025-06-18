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
            summary_text TEXT,
            next_steps TEXT,
            remedy_updates JSON DEFAULT '[]',
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
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS push_tokens (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, token),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS email_unsub_tokens (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY,
            org_name TEXT NOT NULL,
            key TEXT NOT NULL UNIQUE,
            plan TEXT DEFAULT 'free',
            monthly_quota INTEGER DEFAULT 5000,
            requests_this_month INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS channel_subs (
            id INTEGER PRIMARY KEY,
            platform TEXT,
            channel_id TEXT NOT NULL,
            query TEXT NOT NULL,
            source TEXT DEFAULT 'CPSC',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS webhooks (
            id INTEGER PRIMARY KEY,
            api_key_id INTEGER REFERENCES api_keys(id),
            url TEXT NOT NULL,
            query TEXT,
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
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


