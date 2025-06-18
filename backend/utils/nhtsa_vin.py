"""VIN-specific recall helpers using the NHTSA Safety API."""

from __future__ import annotations

from typing import Dict, List
import os
import time
import requests
from sqlalchemy import text

from backend.utils import db as db_utils

VIN_DECODER_URL = os.getenv(
    "VIN_DECODER_URL",
    "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValuesExtended/{vin}?format=json",
)
RECALL_URL = os.getenv(
    "NHTSA_RECALL_URL",
    "https://api.nhtsa.gov/recalls/recallcampaigns?vin={vin}",
)


def _request(url: str) -> Dict:
    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2**attempt)
    return {}


def get_recalls_for_vin(vin: str) -> List[Dict]:
    """Decode a VIN and insert related recalls if new."""
    info = _request(VIN_DECODER_URL.format(vin=vin))
    make = model = year = ""
    results = info.get("Results") or []
    if results:
        first = results[0]
        make = first.get("Make", "")
        model = first.get("Model", "")
        year = first.get("ModelYear", "")
    data = _request(RECALL_URL.format(vin=vin))
    records = data.get("results") or data.get("Results") or []
    recalls: List[Dict] = []
    conn = db_utils.connect()
    trans = conn.begin()
    for r in records:
        rid = str(r.get("NHTSACampaignNumber") or r.get("RecallID"))
        recall = {
            "source": "NHTSA_VIN",
            "id": rid,
            "product": f"{make} {model} {year}".strip(),
            "hazard": r.get("Summary"),
            "recall_date": r.get("ReportReceivedDate") or r.get("RecallDate"),
            "url": r.get("NHTSAActionNumber"),
        }
        existing = conn.execute(
            text("SELECT id FROM recalls WHERE id=:id AND source=:src"),
            {"id": recall["id"], "src": recall["source"]},
        ).fetchone()
        if not existing:
            conn.execute(
                text(
                    "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) "
                    "VALUES (:id, :product, :hazard, :date, :source, :f)"
                ),
                {
                    "id": recall["id"],
                    "product": recall["product"],
                    "hazard": recall["hazard"],
                    "date": recall["recall_date"],
                    "source": recall["source"],
                    "f": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                },
            )
        recalls.append(recall)
    trans.commit()
    conn.close()
    return recalls
