from pathlib import Path
from backend.api.app import create_app, USER_ITEMS
from backend.utils.db import ENGINE


def test_app_routes():
    db = Path("dev.db")
    ENGINE.dispose()
    if db.exists():
        db.unlink()
    app = create_app()
    client = app.test_client()

    # Ensure recalls endpoint returns data
    resp = client.get('/recalls')
    assert resp.status_code == 200
    recalls = resp.get_json()
    assert isinstance(recalls, list)
    assert any(r.get('product') for r in recalls)

    # Add a user item and check alerts
    USER_ITEMS.clear()
    resp = client.post('/user-items', json={'item': 'Widget'})
    assert resp.status_code == 200
    assert 'Widget' in resp.get_json()['items']

    resp = client.get('/alerts')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data['alerts'], list)
    assert any('Widget' in a for a in data['alerts'])


def test_get_recalls(client=None):
    db = Path("dev.db")
    ENGINE.dispose()
    if db.exists():
        db.unlink()
    app = create_app()
    if client is None:
        client = app.test_client()
    r = client.get("/api/recalls?limit=5")
    assert r.status_code == 200
    assert len(r.get_json()) <= 5

