import requests_mock
from backend.utils.fetch_fda_enforcement import fetch_drug_recalls, fetch_device_recalls
from backend.utils.refresh import refresh_recalls
from backend.db import init_db
from backend.utils.db import connect


def test_fda_enforcement_ingest(tmp_path, monkeypatch):
    db = tmp_path / "fda.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db}")
    init_db()

    drug_resp = {
        "results": [
            {
                "recall_number": " D-0001 ",
                "product_description": "Drug A",
                "reason_for_recall": "Contamination",
                "recall_initiation_date": "20240101",
                "link": "http://drug",
            }
        ]
    }
    device_resp = {
        "results": [
            {
                "recall_number": " Z-0002 ",
                "product_description": "Device B",
                "reason_for_recall": "Faulty",
                "recall_initiation_date": "20240202",
                "link": "http://device",
            }
        ]
    }
    with requests_mock.Mocker() as m:
        m.get(
            'https://api.fda.gov/drug/enforcement.json?search=status:"Ongoing"&limit=100',
            json=drug_resp,
        )
        m.get(
            'https://api.fda.gov/device/enforcement.json?search=status:"Ongoing"&limit=100',
            json=device_resp,
        )
        assert fetch_drug_recalls()[0]["id"] == "0001"
        assert fetch_device_recalls()[0]["id"] == "0002"
        # patch other fetchers to return no data
        import backend.utils.refresh as refresh_mod

        monkeypatch.setattr(refresh_mod, "fetch_cpsc", lambda use_cache=False: [])
        monkeypatch.setattr(refresh_mod, "fetch_fda", lambda use_cache=False: [])
        monkeypatch.setattr(refresh_mod, "fetch_nhtsa", lambda use_cache=False: [])
        monkeypatch.setattr(refresh_mod, "fetch_usda", lambda use_cache=False: [])

        refresh_recalls()
        refresh_recalls()

    conn = connect()
    from sqlalchemy import text

    rows = conn.execute(text("SELECT id, source FROM recalls ORDER BY id")).fetchall()
    conn.close()
    assert len(rows) == 3
    sources = {r._mapping["source"] for r in rows}
    assert {"FDA_DRUG", "FDA_DEVICE"}.issubset(sources)
