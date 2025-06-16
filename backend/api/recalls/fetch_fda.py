"""Fetch food recall data from the FDA enforcement API."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json
import requests

API_URL = (
    "https://api.fda.gov/food/enforcement.json?search="
    "report_date:[2023-01-01+TO+2025-12-31]&limit=100"
)
CACHE_FILE = Path(__file__).resolve().parents[3] / "data" / "fda_cache.json"


def _parse(records: List[Dict]) -> List[Dict]:
    parsed: List[Dict] = []
    for r in records:
        recall_id = r.get("recall_number") or r.get("event_id")
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
