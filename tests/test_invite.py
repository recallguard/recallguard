from backend.api.app import create_app
from backend.db import init_db


def test_invite_route(tmp_path, monkeypatch):
    db = tmp_path / 'i.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db}')
    monkeypatch.setenv('SENDGRID_API_KEY', '')
    init_db()
    app = create_app()
    client = app.test_client()

    resp = client.post('/api/auth/signup', json={'email': 'a@b.com', 'password': 'pw'})
    token = resp.get_json()['token']

    resp = client.post(
        '/api/invite',
        json={'email': 'friend@example.com'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert resp.status_code == 200
    assert resp.get_json()['status'] == 'sent'

