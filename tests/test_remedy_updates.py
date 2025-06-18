from backend.tasks import poll_remedy_updates
from backend.db import init_db
from backend.utils.db import connect
from sqlalchemy import text
import requests
import json


def test_poll_remedy_updates(tmp_path, monkeypatch):
    db = tmp_path / "rem.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    init_db()
    conn = connect()
    conn.execute(text("ALTER TABLE recalls ADD COLUMN url TEXT"))
    conn.execute(
        text(
            "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at, remedy_updates, url) "
            "VALUES ('r1','Widget','Fire','2025-05-30','cpsc','2025-05-30','[]','http://x')"
        )
    )
    conn.execute(
        text("INSERT INTO sent_notifications (user_id, recall_id) VALUES (1,'r1')")
    )
    conn.commit()
    conn.close()

    class FakeResp:
        text = "<h2>Remedy</h2><p>Do this</p>"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(requests, "get", lambda *a, **k: FakeResp())

    poll_remedy_updates()

    conn = connect()
    row = conn.execute(
        text("SELECT remedy_updates FROM recalls WHERE id='r1'")
    ).fetchone()
    data = row[0]
    updates = data if isinstance(data, list) else json.loads(data)
    assert len(updates) == 1
    count = conn.execute(text("SELECT COUNT(*) FROM alerts")).fetchone()[0]
    conn.close()
    assert count == 1
