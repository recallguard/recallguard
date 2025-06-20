"""Fetch recalls from the CPSC API with fallback caching."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json
import time
import requests

API_URL = "https://www.saferproducts.gov/RestWebServices/Recall"
DATA_FILE = Path(__file__).resolve().parents[3] / "tests" / "data" / "cpsc_sample.json"


def _parse(records: List[Dict]) -> List[Dict]:
    parsed: List[Dict] = []
    for r in records:
        hazard = None
        hazards = r.get("Hazards") or r.get("Hazard")
        if isinstance(hazards, list) and hazards:
            hazard = hazards[0].get("Name")
        elif isinstance(hazards, str):
            hazard = hazards
        product = r.get("Product")
        if not product:
            prods = r.get("Products")
            if isinstance(prods, list) and prods:
                product = prods[0].get("Name")
        parsed.append(
            {
                "source": "cpsc",
                "id": r.get("RecallID"),
                "product": product,
                "hazard": hazard,
                "recall_date": r.get("RecallDate"),
                "url": r.get("URL"),
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
    offset = 0
    try:
        while True:
            data = _request({"format": "json", "offset": offset})
            records = data.get("results") or data.get("Recalls") or []
            parsed = _parse(records)
            new_records = [r for r in parsed if r["id"] not in seen]
            results.extend(new_records)
            seen.update(r["id"] for r in new_records)
            if not records or len(records) < 100:
                break
            offset += 100
        return results
    except Exception:
        if not use_cache or not DATA_FILE.exists():
            return []
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            records = json.load(fh)
        return _parse(records)
