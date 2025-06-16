"""Fetch food recall data from the FDA enforcement API."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json
import time
import requests

API_URL = "https://api.fda.gov/food/enforcement.json"
CACHE_FILE = Path(__file__).resolve().parents[3] / "data" / "fda_cache.json"


def _parse(records: List[Dict]) -> List[Dict]:
    parsed: List[Dict] = []
    for r in records:
        recall_id = r.get("recall_number") or r.get("event_id")
        title = r.get("product_description")
        parsed.append(
            {
                "source": "fda",
                "id": recall_id,
                "title": title,
                "product": title,
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


def fetch(use_cache: bool = True) -> List[Dict]:
    results: List[Dict] = []
    seen: set[str] = set()
    skip = 0
    try:
        while True:
            data = _request({"search": "report_date:[2023-01-01+TO+2025-12-31]", "limit": 100, "skip": skip})
            records = data.get("results") or []
            parsed = _parse(records)
            new_records = [r for r in parsed if r["id"] not in seen]
            results.extend(new_records)
            seen.update(r["id"] for r in new_records)
            if not records or len(records) < 100:
                break
            skip += 100
        CACHE_FILE.write_text(json.dumps(records), encoding="utf-8")
        return results
    except Exception:
        if use_cache and CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                return _parse(data)
            except Exception:
                return []
        return []
