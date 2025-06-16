from backend.api.app import create_app
from backend.db import init_db
from backend.utils.auth import decode_access_token


def setup(tmp_path, monkeypatch):


    db = tmp_path / 'auth.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db}')

    init_db()
    app = create_app()
    return app.test_client()


def test_signup_and_login(tmp_path, monkeypatch):
    client = setup(tmp_path, monkeypatch)
    resp = client.post('/api/auth/signup', json={'email': 'a@a.com', 'password': 'pw'})
    assert resp.status_code == 201
    data = resp.get_json()
    payload = decode_access_token(data['token'])
    assert payload['user_id'] == data['user_id']

    resp = client.post('/api/auth/login', json={'email': 'a@a.com', 'password': 'bad'})
    assert resp.status_code == 401


def test_recall_requires_token(tmp_path, monkeypatch):
    client = setup(tmp_path, monkeypatch)
    resp = client.post('/api/auth/signup', json={'email': 'b@b.com', 'password': 'pw'})
    token = resp.get_json()['token']

    assert client.get('/api/recalls/recent').status_code == 401

    resp = client.get('/api/recalls/recent', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
