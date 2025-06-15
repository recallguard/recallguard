
from backend.api.recalls.fetch_cpsc import fetch


def test_fetch_cpsc():
    recalls = fetch()
    assert len(recalls) >= 1
    assert any(r["product"] == "Widget" for r in recalls)

from backend.api.recalls import fetch_cpsc
import requests


def test_fetch_cpsc(monkeypatch):
    """Ensure the fetcher returns data even when the API request fails."""
    def fake_get(*args, **kwargs):
        raise requests.exceptions.RequestException("blocked")

    monkeypatch.setattr(requests, "get", fake_get)
    recalls = fetch_cpsc()
    assert len(recalls) >= 1
    assert any(r["product"] == "Widget" for r in recalls)
    assert any(r["hazard"] == "Fire" for r in recalls)
    assert any(r["recall_date"] == "2024-04-01" for r in recalls)

