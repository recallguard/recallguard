"""Database initialization helpers."""
from backend.utils.session import get_engine
from sqlalchemy import text
from .models import metadata
from .seed_data import seed


def init_db() -> None:
    """Create tables if they do not exist."""
    metadata.create_all(bind=get_engine())
    with get_engine().connect() as conn:
        if not conn.execute(text('SELECT COUNT(*) FROM users')).fetchone()[0]:
            seed()
