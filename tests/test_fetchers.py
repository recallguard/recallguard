import requests
from backend.utils.refresh import refresh_recalls
from backend.db import init_db
from backend.utils.db import connect

class FakeResponse:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data

def fake_get(url, params=None, timeout=10):
    key = (
        params.get("offset") if params and "offset" in params else params.get("skip") if params and "skip" in params else params.get("page", 0)
    )
    if key not in (0, None):
        return FakeResponse({"results": []})

    if "saferproducts" in url:
        data = {"results": [{"RecallID": "1", "Product": "Widget", "Hazards": [{"Name": "Fire"}], "RecallDate": "2025-05-30"}]}
    elif "api.fda.gov" in url:
        data = {"results": [{"recall_number": "F-001", "product_description": "Food", "reason_for_recall": "Salmonella", "recall_initiation_date": "20250530"}]}
    elif "nhtsa" in url:
        data = {"results": [{"NHTSACampaignNumber": "22V123", "Component": "Engine", "Summary": "Stall", "ReportReceivedDate": "2025-05-30"}]}
    else:
        data = {"results": [{"id": "R-1", "product_description": "Meat", "reason_for_recall": "Ecoli", "recall_initiation_date": "20250530"}]}
    return FakeResponse(data)

def test_fetchers_insert(tmp_path, monkeypatch):


    db = tmp_path / 't.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db}')

    init_db()
    monkeypatch.setattr(requests, 'get', fake_get)
    refresh_recalls()
    conn = connect()
    from sqlalchemy import text
    count = conn.execute(text('SELECT COUNT(*) FROM recalls')).fetchone()[0]
    conn.close()
    assert count >= 1

