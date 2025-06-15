"""Fetch food recall data from the FDA enforcement API.

This module retrieves recent food recalls from the public FDA API. Results are
cached to ``data/fda_cache.json`` so the application can operate without
network access. Each recall entry is normalized to include ``id``, ``title``,
``hazard``, ``recall_date``, and ``url``.
"""

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
    """Normalize raw FDA records to RecallGuard's schema."""
    parsed: List[Dict] = []
    for r in records:
        recall_id = r.get("recall_number") or r.get("event_id")
        parsed.append(
            {
                "source": "FDA",
                "id": recall_id,
                "title": r.get("product_description"),
                "hazard": r.get("reason_for_recall"),
                "recall_date": r.get("recall_initiation_date") or r.get("report_date"),
                "url": r.get("more_code_info")
                or f"https://www.fda.gov/safety/recalls-market-withdrawals-safety-alerts/{recall_id}",
            }
        )
    return parsed


def fetch() -> List[Dict]:
    """Return a list of FDA recalls using a cached fallback."""
    try:
        response = requests.get(API_URL, timeout=10)
        response.raise_for_status()
        data = response.json().get("results", [])
        parsed = _parse(data)
        try:
            CACHE_FILE.write_text(json.dumps(data), encoding="utf-8")
        except Exception:
            pass
        return parsed
    except Exception:
        if CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                return _parse(data)
            except Exception:
                return []
        return []
