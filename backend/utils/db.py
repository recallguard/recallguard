"""Database helper using SQLAlchemy engine."""
from sqlalchemy.engine import Connection
from backend.utils.session import get_engine


def connect() -> Connection:
    return get_engine().connect()
