"""Fetch recalls from the CPSC API with a local fallback."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json
import requests

API_URL = "https://www.saferproducts.gov/RestWebServices/Recall?format=json"
DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "cpsc_sample.json"


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
        parsed.append({
            "source": "cpsc",
            "id": r.get("RecallID"),
            "product": product,
            "hazard": hazard,
            "recall_date": r.get("RecallDate"),
            "url": r.get("URL"),
        })
    return parsed


def fetch() -> List[Dict]:
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        records = response.json()
        if isinstance(records, dict):
            records = records.get("results") or records.get("Recalls") or []
        return _parse(records)
    except Exception:
        if not DATA_FILE.exists():
            return []
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            records = json.load(fh)
        return _parse(records)
