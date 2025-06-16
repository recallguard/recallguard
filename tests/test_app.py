from backend.api.app import create_app, USER_ITEMS
import backend.api.recalls as recall_mod
import backend.api.app as app_mod


def test_app_routes(tmp_path, monkeypatch):
    monkeypatch.setattr(recall_mod, "fetch_all", lambda use_cache=True: [{"product": "Widget"}])
    monkeypatch.setattr(app_mod, "fetch_all", recall_mod.fetch_all)
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
