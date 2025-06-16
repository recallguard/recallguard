"""Fetch food recall data from the FDA enforcement API."""
from __future__ import annotations

from typing import Dict, List
<<<<<<< HEAD
import json
=======
import time
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
import requests

API_URL = "https://api.fda.gov/food/enforcement.json"


def _parse(records: List[Dict]) -> List[Dict]:
    parsed: List[Dict] = []
    for r in records:
        recall_id = r.get("recall_number") or r.get("event_id")
<<<<<<< HEAD
        parsed.append({
            "source": "fda",
            "id": recall_id,
            "title": r.get("product_description"),
            "hazard": r.get("reason_for_recall"),
            "recall_date": r.get("recall_initiation_date") or r.get("report_date"),
            "url": r.get("more_code_info") or f"https://www.fda.gov/{recall_id}",
        })
    return parsed



def fetch(use_cache: bool = True) -> List[Dict]:
=======
def fetch() -> List[Dict]:

    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json().get("results", [])
        parsed = _parse(data)
        CACHE_FILE.write_text(json.dumps(data), encoding="utf-8")
        return parsed
    except Exception:
        if use_cache and CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                return _parse(data)
            except Exception:
                return []
        return []
=======
        parsed.append(
            {
                "source": "fda",
                "id": recall_id,
                "product": r.get("product_description"),
                "hazard": r.get("reason_for_recall"),
                "recall_date": r.get("recall_initiation_date") or r.get("report_date"),
                "url": r.get("more_code_info") or f"https://www.fda.gov/{recall_id}",
            }
        )
    return parsed


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


def fetch(use_cache: bool = False) -> List[Dict]:
    results: List[Dict] = []
    seen: set[str] = set()
    skip = 0
    while True:
        data = _request(
            {
                "search": "report_date:[2023-01-01+TO+2025-12-31]",
                "limit": 100,
                "skip": skip,
            }
        )
        records = data.get("results") or []
        parsed = _parse(records)
        new_records = [r for r in parsed if r["id"] not in seen]
        results.extend(new_records)
        seen.update(r["id"] for r in new_records)
        if not records or len(records) < 100:
            break
        skip += 100
    return results
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
