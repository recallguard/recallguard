from pathlib import Path
from backend.api.recalls import fetch_fda
from backend.db import create_tables
from backend.db.models import Recall
from backend.utils.db import get_session, ENGINE
import requests
import json


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "fda_cache.json"


def test_fetch_fda(monkeypatch):
    """Ensure the FDA fetcher falls back to cached data when the request fails."""

    # Ensure the cache contains predictable data
    DATA_FILE.write_text(
        json.dumps([
            {
                "recall_number": "F-0010-2024",
                "product_description": "Sample Food Recall",
                "reason_for_recall": "Possible Salmonella contamination",
                "recall_initiation_date": "20240401",
                "more_code_info": "https://example.com/fda-recall1",
            }
        ])
    )

    def fake_get(*args, **kwargs):
        raise requests.exceptions.RequestException("blocked")

    db = Path("dev.db")
    ENGINE.dispose()
    if db.exists():
        db.unlink()
    create_tables()
    monkeypatch.setattr(requests, "get", fake_get)
    recalls = fetch_fda()
    assert len(recalls) >= 1
    assert isinstance(recalls[0], Recall)
    with get_session() as session:
        assert session.query(Recall).count() >= 1
