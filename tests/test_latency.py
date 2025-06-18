from backend.api.app import create_app
from backend.db import init_db
from backend.utils.db import connect
from sqlalchemy import text


def test_latency_endpoint(tmp_path, monkeypatch):
    db = tmp_path / "lat.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    init_db()
    conn = connect()
    conn.execute(text("DELETE FROM recalls"))
    conn.execute(text("INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) VALUES ('1','a','', '2024-01-01','cpsc','2024-01-02')"))
    conn.execute(text("INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) VALUES ('2','b','', '2024-01-01','cpsc','2024-01-04')"))
    conn.commit()
    conn.close()
    app = create_app()
    client = app.test_client()
    resp = client.get('/latency')
    assert resp.status_code == 200
    data = resp.get_json()
    assert abs(data['average_latency_seconds'] - 172800) < 1
