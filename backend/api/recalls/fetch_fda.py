"""Fetch food recall data from the FDA enforcement API.

This module retrieves recent food recalls from the public FDA API. Results are
cached to ``data/fda_cache.json`` so the application can operate without
network access. Each recall entry is normalized to include ``id``, ``title``,
``hazard``, ``recall_date``, and ``url``.
"""

from __future__ import annotations

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Dict, List
import json

import requests
from sqlalchemy import select

from backend.db.models import Recall
from backend.utils.db import get_session

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


def _store(records: List[Dict]) -> List[Recall]:
    """Upsert parsed recalls into the database and return ORM objects."""
    recalls: List[Recall] = []
    with get_session() as session:
        for r in records:
            rd: date | None = None
            if r.get("recall_date"):
                try:
                    rd = date.fromisoformat(str(r["recall_date"]))
                except ValueError:
                    rd = None
            stmt = select(Recall).where(
                Recall.source == r["source"],
                Recall.product == r["title"],
                Recall.recall_date == rd,
            )
            obj = session.scalars(stmt).first()
            if obj:
                obj.hazard = r.get("hazard")
                obj.details_url = r.get("url")
                obj.raw_json = json.dumps(r)
            else:
                obj = Recall(
                    source=r["source"],
                    product=r["title"],
                    hazard=r.get("hazard"),
                    recall_date=rd,
                    details_url=r.get("url"),
                    raw_json=json.dumps(r),
                )
                session.add(obj)
            recalls.append(obj)
    return recalls


def fetch() -> List[Recall]:
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
        return _store(parsed)
    except Exception:
        if CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                return _store(_parse(data))
            except Exception:
                return []
        return []
