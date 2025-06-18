"""Fetch drug and device recall data from openFDA."""

from __future__ import annotations

from typing import Dict, List
import os
import time
import requests

DRUG_URL = os.getenv(
    "FDA_DRUG_URL",
    "https://api.fda.gov/drug/enforcement.json?search=status:%22Ongoing%22&limit=100",
)
DEVICE_URL = os.getenv(
    "FDA_DEVICE_URL",
    "https://api.fda.gov/device/enforcement.json?search=status:%22Ongoing%22&limit=100",
)


def _request(url: str, params: Dict | None = None) -> Dict:
    for attempt in range(3):
        try:
            resp = requests.get(url, params=params or {}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2**attempt)
    return {}


def _parse(records: List[Dict], source: str) -> List[Dict]:
    parsed: List[Dict] = []
    for r in records:
        recall_id = str(r.get("recall_number", "")).strip()
        recall_id = "".join(ch for ch in recall_id if ch.isdigit())
        parsed.append(
            {
                "source": source,
                "id": recall_id,
                "product": r.get("product_description"),
                "hazard": r.get("reason_for_recall"),
                "recall_date": r.get("recall_initiation_date"),
                "url": r.get("link"),
                "details": {"code_info": r.get("more_code_info") or r.get("code_info")},
            }
        )
    return parsed


def fetch_drug_recalls() -> List[Dict]:
    data = _request(DRUG_URL)
    records = data.get("results") or []
    return _parse(records, "FDA_DRUG")


def fetch_device_recalls() -> List[Dict]:
    data = _request(DEVICE_URL)
    records = data.get("results") or []
    return _parse(records, "FDA_DEVICE")
