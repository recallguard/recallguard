from backend.api.app import create_app
from backend.db import init_db
from backend.utils.db import connect
from sqlalchemy import text


def setup_client(tmp_path, monkeypatch):
    db = tmp_path / "bill.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    init_db()
    app = create_app()
    return app.test_client()


def test_webhook_plan_change(tmp_path, monkeypatch):
    client = setup_client(tmp_path, monkeypatch)
    payload = {
        "type": "customer.subscription.updated",
        "data": {"object": {"metadata": {"user_id": 1, "plan": "pro", "seats": 1}}},
    }
    client.post("/api/stripe/webhook", json=payload)
    conn = connect()
    plan = conn.execute(text("SELECT plan FROM stripe_customers WHERE user_id=1")).fetchone()[0]
    conn.close()
    assert plan == "pro"


def test_quota_block(tmp_path, monkeypatch):
    client = setup_client(tmp_path, monkeypatch)
    conn = connect()
    conn.execute(text("UPDATE stripe_customers SET quota=1 WHERE user_id=1"))
    conn.commit()
    conn.close()
    login = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password"})
    token = login.get_json()["token"]
    client.get("/api/recalls/recent", headers={"Authorization": f"Bearer {token}"})
    resp = client.get("/api/recalls/recent", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 429
