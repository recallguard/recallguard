from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from backend.config import settings

_engine = None
SessionLocal = scoped_session(sessionmaker(autoflush=False))


def get_engine():
    global _engine
    if _engine is None or str(_engine.url) != settings.database_url:
        _engine = create_engine(settings.database_url, future=True)
        SessionLocal.configure(bind=_engine)
        original = _engine.dispose

        def _dispose_and_mark(*args, **kwargs):
            _engine._disposed = True
            return original(*args, **kwargs)

        _engine.dispose = _dispose_and_mark  # type: ignore
        _engine._disposed = False
    return _engine
