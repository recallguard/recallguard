
from __future__ import annotations

from datetime import date
from typing import Dict, List

from sqlalchemy import select

from backend.db.models import Recall
from backend.utils.db import get_session
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
                Recall.product == r["product"],
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
                    product=r["product"],
                    hazard=r.get("hazard"),
                    recall_date=rd,
                    details_url=r.get("url"),
                    raw_json=json.dumps(r),
                )
                session.add(obj)
            recalls.append(obj)
    return recalls


def fetch() -> List[Recall]:
        return _store(_parse(records))
        return _store(_parse(records))
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

"""Fetch recalls from the CPSC API."""
from typing import List, Dict


def fetch() -> List[Dict]:
    """Return a list of recalls from the CPSC.

    This is a placeholder implementation that would normally call the
    official CPSC API.
    """
    return [{"source": "CPSC", "title": "Sample recall", "product": "Widget"}]


