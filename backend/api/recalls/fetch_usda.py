"""Fetch recalls from the USDA."""
from __future__ import annotations

from typing import List
import json

from sqlalchemy import select

from backend.db.models import Recall
from backend.utils.db import get_session


def fetch() -> List[Recall]:
    """Return a list of food recalls from the USDA.
    Placeholder data is used in tests.
    """
    records = [
        {
            "source": "USDA",
            "title": "Food recall",
            "product": "Spinach",
            "hazard": None,
            "recall_date": None,
            "url": None,
        }
    ]
    recalls: List[Recall] = []
    with get_session() as session:
        for r in records:
            stmt = select(Recall).where(
                Recall.source == r["source"],
                Recall.product == r["product"],
                Recall.recall_date.is_(None),
            )
            obj = session.scalars(stmt).first()
            if obj:
                obj.raw_json = json.dumps(r)
            else:
                obj = Recall(
                    source=r["source"],
                    product=r["product"],
                    raw_json=json.dumps(r),
                )
                session.add(obj)
            recalls.append(obj)
    return recalls

