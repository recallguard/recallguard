from backend.api.app import create_app
from backend.db import init_db
from backend.utils.db import connect
from sqlalchemy import text


def test_check_route(tmp_path, monkeypatch):
    db = tmp_path / "scan.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    init_db()
    conn = connect()
    conn.execute(
        text(
            "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) VALUES ('R1','12345','Danger','2024-01-01','cpsc','2024-01-01')"
        )
    )
    conn.commit()
    conn.close()

    app = create_app()
    client = app.test_client()

    resp = client.get("/api/check/12345")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "recalled"
    assert data["recall_id"] == "R1"

    resp = client.get("/api/check/999")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "safe"
