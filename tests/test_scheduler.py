import pytest
from freezegun import freeze_time

from backend.api.app import create_app
from backend.db import init_db
from backend.utils.db import connect
from backend.utils.refresh import refresh_recalls



@pytest.mark.integration
@freeze_time("2025-06-01")
def test_manual_refresh_and_idempotent(tmp_path, monkeypatch):
    db = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    init_db()

    sample = [{"id": 99, "product": "Toy", "hazard": "Choking", "recall_date": "2025-05-30", "source": "cpsc"}]
    import backend.utils.refresh as refresh_mod
    monkeypatch.setattr(refresh_mod, "fetch_cpsc", lambda use_cache=False: sample)
    monkeypatch.setattr(refresh_mod, "fetch_fda", lambda use_cache=False: [])
    monkeypatch.setattr(refresh_mod, "fetch_nhtsa", lambda use_cache=False: [])
    monkeypatch.setattr(refresh_mod, "fetch_usda", lambda use_cache=False: [])

    app = create_app()
    client = app.test_client()
    login = client.post('/api/auth/login', json={'email': 'user@example.com', 'password': 'password'})
    token = login.get_json()['token']

    resp = client.post(
        "/api/recalls/refresh",
        headers={"X-Admin": "true", "Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200

    conn = connect()
    from sqlalchemy import text
    count1 = conn.execute(text("SELECT COUNT(*) FROM recalls")).fetchone()[0]
    conn.close()
    assert count1 >= 1

    refresh_recalls()
    conn = connect()
    count2 = conn.execute(text("SELECT COUNT(*) FROM recalls")).fetchone()[0]
    conn.close()
    assert count2 == count1
