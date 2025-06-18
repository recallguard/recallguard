"""Seed database with example data."""
from datetime import datetime
from pathlib import Path
import sqlite3
from sqlalchemy import text

from backend.utils.auth import hash_password
from backend.utils.session import get_engine


def seed() -> None:
    """Seed example records using the SQLAlchemy engine."""
    with get_engine().begin() as conn:
        conn.execute(
            text(
                "INSERT INTO users (email, password_hash, created_at, email_opt_in) VALUES (:e, :p, :c, 1)"
            ),
            {"e": "user@example.com", "p": hash_password("password"), "c": datetime.utcnow().isoformat()},
        )
        conn.execute(text("INSERT INTO products (name, user_id) VALUES (:n, :u)"), {"n": "Widget", "u": 1})
        conn.execute(
            text(
                "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) VALUES (:i, :p, :h, :d, :s, :f)"
            ),
            {
                "i": "demo-1",
                "p": "Widget",
                "h": "Fire hazard",
                "d": "2024-04-01",
                "s": "cpsc",
                "f": datetime.utcnow().isoformat(),
            },
        )
        conn.execute(
            text(
                "INSERT INTO subscriptions (user_id, recall_source, product_query) VALUES (1, 'cpsc', 'Widget')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO api_keys (org_name, key, plan) VALUES (:n, :k, 'free')"
            ),
            {"n": "Demo Org", "k": "demo-key"},
        )
        conn.execute(
            text(
                "INSERT INTO stripe_customers (user_id, plan, quota, seats) VALUES (1, 'free', 100, 1)"
            )
        )


def seed_path(db_path: Path) -> None:
    """Seed example records using a direct SQLite connection."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
        ("user@example.com", hash_password("password"), datetime.utcnow().isoformat()),
    )
    cur.execute("INSERT INTO products (name, user_id) VALUES (?, ?)", ("Widget", 1))
    cur.execute(
        "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) VALUES (?, ?, ?, ?, ?, ?)",
        (
            "demo-1",
            "Widget",
            "Fire hazard",
            "2024-04-01",
            "cpsc",
            datetime.utcnow().isoformat(),
        ),
    )
    cur.execute(
        "INSERT INTO api_keys (org_name, key, plan) VALUES (?, ?, 'free')",
        ("Demo Org", "demo-key"),
    )
    cur.execute(
        "INSERT INTO stripe_customers (user_id, plan, quota, seats) VALUES (1, 'free', 100, 1)"
    )
    conn.commit()
    conn.close()
