from backend.api.app import create_app
from backend.db import init_db
from backend.utils.db import connect
from sqlalchemy import text


def setup_client(tmp_path, monkeypatch):
    db = tmp_path / "items.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    init_db()
    app = create_app()
    client = app.test_client()
    signup = client.post('/api/auth/signup', json={'email': 'a@b.com', 'password': 'pw'})
    token = signup.get_json()['token']
    return client, token


def test_add_list_delete_items(tmp_path, monkeypatch):
    client, token = setup_client(tmp_path, monkeypatch)
    resp = client.post('/api/items', json={'upc': '12345', 'label': 'Toy'}, headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 201
    item_id = resp.get_json()['id']
    resp = client.get('/api/items', headers={'Authorization': f'Bearer {token}'})
    data = resp.get_json()
    assert data and data[0]['upc'] == '12345'
    assert data[0]['status'] == 'safe'
    resp = client.delete(f'/api/items/{item_id}', headers={'Authorization': f'Bearer {token}'})
    assert resp.status_code == 200
    resp = client.get('/api/items', headers={'Authorization': f'Bearer {token}'})
    assert resp.get_json() == []


def test_item_recalled_status(tmp_path, monkeypatch):
    client, token = setup_client(tmp_path, monkeypatch)
    conn = connect()
    conn.execute(text("INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) VALUES ('R1','111','Danger','2024-01-01','cpsc','2024-01-01')"))
    conn.commit()
    conn.close()
    client.post('/api/items', json={'upc': '111'}, headers={'Authorization': f'Bearer {token}'})
    resp = client.get('/api/items', headers={'Authorization': f'Bearer {token}'})
    assert resp.get_json()[0]['status'] == 'recalled'
