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
