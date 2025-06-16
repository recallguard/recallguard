"""Fetch recalls from the NHTSA API."""
from __future__ import annotations

from typing import Dict, List
import time
import requests

API_URL = "https://api.nhtsa.gov/Recalls/vehicle"


<<<<<<< HEAD
def fetch(use_cache: bool = True) -> List[Dict]:
    """Return vehicle-related recalls.
    This placeholder would normally call the NHTSA API.
    """
    return [{"source": "NHTSA", "title": "Vehicle recall", "product": "Car"}]
=======
def _request(params: Dict) -> Dict:
    for attempt in range(3):
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def _parse(records: List[Dict]) -> List[Dict]:
    parsed: List[Dict] = []
    for r in records:
        parsed.append(
            {
                "source": "nhtsa",
                "id": str(r.get("NHTSACampaignNumber") or r.get("RecallID")),
                "product": r.get("Component") or r.get("Model"),
                "hazard": r.get("Summary"),
                "recall_date": r.get("ReportReceivedDate"),
                "url": r.get("NHTSAActionNumber"),
            }
        )
    return parsed


def fetch(use_cache: bool = False) -> List[Dict]:
    results: List[Dict] = []
    seen: set[str] = set()
    page = 1
    while True:
        data = _request({"format": "json", "page": page})
        records = data.get("results") or data.get("Results") or []
        parsed = _parse(records)
        new_records = [r for r in parsed if r["id"] not in seen]
        results.extend(new_records)
        seen.update(r["id"] for r in new_records)
        if not records or len(records) < 100:
            break
        page += 1
    return results
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)

