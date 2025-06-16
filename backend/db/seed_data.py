"""Seed database with example data."""
import sqlite3
from pathlib import Path
from datetime import datetime

from backend.utils.auth import hash_password


def seed(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
        (
            "user@example.com",
            hash_password("password"),
            datetime.utcnow().isoformat(),
        ),
    )
    cur.execute("INSERT INTO products (name, user_id) VALUES (?, ?)", ("Widget", 1))
    cur.execute(
        "INSERT INTO recalls (product, hazard, recall_date, source) VALUES (?, ?, ?, ?)",
        ("Widget", "Fire hazard", "2024-04-01", "cpsc"),
    )
    conn.commit()
    conn.close()

