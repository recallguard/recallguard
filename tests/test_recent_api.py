from backend.api.app import create_app
from backend.db import init_db


def setup_db(tmp_path, monkeypatch):
    db = tmp_path / 'rg.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db}')
    init_db()


def test_recent_and_user_endpoints(tmp_path, monkeypatch):
    setup_db(tmp_path, monkeypatch)
    app = create_app()
    client = app.test_client()

    login = client.post('/api/auth/login', json={'email': 'user@example.com', 'password': 'password'})
    token = login.get_json()['token']

    resp = client.get('/api/recalls/recent', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(r['product'] == 'Widget' for r in data)

    resp = client.get('/api/recalls/user/1', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(r['product'] == 'Widget' for r in data)
