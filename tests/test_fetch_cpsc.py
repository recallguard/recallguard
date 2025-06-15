from backend.api.recalls.fetch_cpsc import fetch


def test_fetch_cpsc():
    recalls = fetch()
    assert len(recalls) >= 1
    assert any(r["product"] == "Widget" for r in recalls)
