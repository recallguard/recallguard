"""SQLAlchemy database utilities."""
from __future__ import annotations

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_database_url

ENGINE = create_engine(get_database_url(), future=True)
SessionLocal = sessionmaker(bind=ENGINE, expire_on_commit=False, class_=Session)


@contextmanager
def get_session() -> Session:
    """Provide a transactional session scope."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
