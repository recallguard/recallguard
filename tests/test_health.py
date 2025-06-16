from backend.api.app import create_app
from backend.db import init_db


def setup_app(tmp_path, monkeypatch):


    db = tmp_path / 'health.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db}')

    init_db()
    app = create_app()
    return app.test_client(), app


def test_health_ok(tmp_path, monkeypatch):
    client, _ = setup_app(tmp_path, monkeypatch)
    resp = client.get('/healthz')
    assert resp.status_code == 200
    assert resp.get_json()['db'] == 'ok'


def test_health_db_down(tmp_path, monkeypatch):
    client, app = setup_app(tmp_path, monkeypatch)
    from backend.utils.session import get_engine
    get_engine().dispose()
    resp = client.get('/healthz')
    assert resp.status_code == 503
