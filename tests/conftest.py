import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.db.models import metadata
import backend.utils.session as session_mod

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(autouse=True)
def db_session(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", TEST_DB_URL)
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    original = engine.dispose

    def _dispose_and_mark(*args, **kwargs):
        engine._disposed = True
        return original(*args, **kwargs)

    engine.dispose = _dispose_and_mark  # type: ignore
    engine._disposed = False

    monkeypatch.setattr(session_mod, "_engine", engine, raising=False)
    monkeypatch.setattr(session_mod, "get_engine", lambda: engine)
    monkeypatch.setattr("backend.db.get_engine", lambda: engine)
    monkeypatch.setattr("backend.db.seed_data.get_engine", lambda: engine)
    monkeypatch.setattr("backend.api.ops.get_engine", lambda: engine)
    monkeypatch.setattr("backend.utils.db.get_engine", lambda: engine)
    session_mod.SessionLocal.configure(bind=engine)
    metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()
    metadata.drop_all(bind=engine)
    session_mod.SessionLocal.remove()
    engine.dispose()
    session_mod._engine = None
