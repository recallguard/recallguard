from __future__ import annotations

from typing import Dict, List
import time
import requests

API_URL = "https://www.fsis.usda.gov/external-portal-data/recalls"


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
                "source": "usda",
                "id": str(r.get("id") or r.get("RecallNumber")),
                "product": r.get("product_description") or r.get("Product"),
                "hazard": r.get("reason_for_recall") or r.get("hazard"),
                "recall_date": r.get("recall_initiation_date") or r.get("RecallDate"),
                "url": r.get("url"),
            }
        )
    return parsed


def fetch(use_cache: bool = False) -> List[Dict]:
    results: List[Dict] = []
    seen: set[str] = set()
    page = 0
    while True:
        data = _request({"page": page})
        records = data.get("results") or data.get("recalls") or []
        parsed = _parse(records)
        new_records = [r for r in parsed if r["id"] not in seen]
        results.extend(new_records)
        seen.update(r["id"] for r in new_records)
        if not records or len(records) < 100:
            break
        page += 1
    return results
