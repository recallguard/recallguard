# backend/utils/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# SQLite needs that extra arg; Postgres/MySQL do not
connect_args = {"check_same_thread": False} if settings.DATABASE_URI.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URI, echo=True, connect_args=connect_args)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    """Yield a database session, closing it at the end of the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
