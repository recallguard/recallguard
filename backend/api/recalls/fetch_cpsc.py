"""Fetch recalls from the CPSC recall API.

This module attempts to retrieve live recall data from
``saferproducts.gov``. If the request fails (for example when running in an
environment without external network access), it falls back to sample data
stored locally in ``data/cpsc_sample.json``. The returned records are
normalized to a common schema used throughout RecallGuard.
"""

from pathlib import Path
from typing import List, Dict
import json

import requests


API_URL = "https://www.saferproducts.gov/RestWebServices/Recall?format=json"
DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "cpsc_sample.json"


def _parse(records: List[Dict]) -> List[Dict]:
    """Normalize recall records to a consistent structure."""
    parsed: List[Dict] = []
    for r in records:
        hazards = r.get("Hazards") or r.get("Hazard")
        hazard = None
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
                "source": "CPSC",
                "id": r.get("RecallID"),
                "title": r.get("Title"),
                "product": product,
                "hazard": hazard,
                "recall_date": r.get("RecallDate"),
                "url": r.get("URL"),
            }
        )
    return parsed


def fetch() -> List[Dict]:
    """Return a list of recalls from the CPSC API or sample data."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        payload = response.json()
        records = (
            payload.get("results")
            or payload.get("Results")
            or payload.get("recalls")
            or payload
        )
        if isinstance(records, dict):
            records = records.get("Recalls") or []
        if not isinstance(records, list):
            records = []
        return _parse(records)
    except Exception:
        if not DATA_FILE.exists():
            return []
        with DATA_FILE.open("r", encoding="utf-8") as fh:
            records = json.load(fh)
        return _parse(records)

