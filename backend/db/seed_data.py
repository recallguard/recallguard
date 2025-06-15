"""Seed database with example data."""
import sqlite3
from pathlib import Path


def seed(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (email) VALUES (?)", ("user@example.com",))
    cur.execute("INSERT INTO products (name, user_id) VALUES (?, ?)", ("Widget", 1))
    cur.execute(
        "INSERT INTO recalls (product, hazard, recall_date, source) VALUES (?, ?, ?, ?)",
        ("Widget", "Fire hazard", "2024-04-01", "cpsc"),
    )
    conn.commit()
    conn.close()

