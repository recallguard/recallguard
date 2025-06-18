from backend.api.app import create_app
from backend.db import init_db
from backend.utils.session import SessionLocal
from sqlalchemy import text


def setup_client(tmp_path, monkeypatch):
    db = tmp_path / 'partner.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db}')
    init_db()
    with SessionLocal() as dbs:
        dbs.execute(
            text("INSERT INTO api_keys (org_name, key, plan) VALUES ('Test','abc','free')")
        )
        dbs.commit()
    app = create_app()
    return app.test_client()


def test_recalls_requires_key(tmp_path, monkeypatch):
    client = setup_client(tmp_path, monkeypatch)
    assert client.get('/v1/recalls').status_code == 401
    resp = client.get('/v1/recalls', headers={'X-Api-Key': 'abc'})
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
