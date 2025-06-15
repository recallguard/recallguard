from backend.api.app import create_app
from backend.db import init_db


def setup_db(tmp_path):
    db = tmp_path / 'rg.db'
    init_db(db)
    return db


def test_recent_and_user_endpoints(tmp_path, monkeypatch):
    db = setup_db(tmp_path)
    monkeypatch.setenv('RECALLGUARD_DB', str(db))
    app = create_app()
    client = app.test_client()

    resp = client.get('/api/recalls/recent')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(r['product'] == 'Widget' for r in data)

    resp = client.get('/api/recalls/user/1')
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(r['product'] == 'Widget' for r in data)
