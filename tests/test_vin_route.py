import requests_mock
from backend.api.app import create_app
from backend.db import init_db
from backend.utils.db import connect


def test_vin_route(tmp_path, monkeypatch):
    db = tmp_path / "vin.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    init_db()

    vin = "12345678901234567"
    decode_url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{vin}?format=json"
    recall_url = f"https://api.nhtsa.gov/recalls/recallcampaigns?vin={vin}"
    decode_resp = {"Results": [{"Make": "Ford", "Model": "F150", "ModelYear": "2020"}]}
    recall_resp = {
        "results": [
            {
                "NHTSACampaignNumber": "20V123",
                "Summary": "Issue",
                "ReportReceivedDate": "20240101",
                "NHTSAActionNumber": "http://recall",
            }
        ]
    }

    with requests_mock.Mocker() as m:
        m.get(decode_url, json=decode_resp)
        m.get(recall_url, json=recall_resp)
        app = create_app()
        client = app.test_client()
        login = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "password"},
        )
        token = login.get_json()["token"]
        resp = client.get(
            f"/api/recalls/vin/{vin}", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data and data[0]["id"] == "20V123"

        # call again to ensure no duplicate insert
        resp = client.get(
            f"/api/recalls/vin/{vin}", headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200

    conn = connect()
    from sqlalchemy import text

    count = conn.execute(
        text('SELECT COUNT(*) FROM recalls WHERE source="NHTSA_VIN"')
    ).fetchone()[0]
    conn.close()
    assert count == 1
