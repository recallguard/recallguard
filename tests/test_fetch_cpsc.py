from pathlib import Path
from backend.api.recalls import fetch_cpsc
from backend.db import create_tables
from backend.db.models import Recall
from backend.utils.db import get_session, ENGINE
import requests


def test_fetch_cpsc(monkeypatch):
    """Ensure the fetcher returns data even when the API request fails."""
    def fake_get(*args, **kwargs):
        raise requests.exceptions.RequestException("blocked")

    db = Path("dev.db")
    ENGINE.dispose()
    if db.exists():
        db.unlink()
    create_tables()
    monkeypatch.setattr(requests, "get", fake_get)
    recalls = fetch_cpsc()
    assert len(recalls) >= 1
    assert isinstance(recalls[0], Recall)
    with get_session() as session:
        assert session.query(Recall).count() >= 1
