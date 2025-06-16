"""Seed database with example data."""
from datetime import datetime
from sqlalchemy import text
from backend.utils.auth import hash_password
from backend.utils.session import get_engine


def seed() -> None:
    with get_engine().begin() as conn:
        conn.execute(
            text(
                "INSERT INTO users (email, password_hash, created_at, email_opt_in) VALUES (:e, :p, :c, 1)"
            ),
            {"e": "user@example.com", "p": hash_password("password"), "c": datetime.utcnow().isoformat()},
        )
        conn.execute(
            text("INSERT INTO products (name, user_id) VALUES (:n, :u)"),
            {"n": "Widget", "u": 1},
        )
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
