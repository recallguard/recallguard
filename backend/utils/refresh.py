"""Data refresh utilities."""

from __future__ import annotations

from typing import Dict, List
from datetime import datetime


import os
from sqlalchemy import text


from backend.api.recalls import fetch_cpsc, fetch_fda, fetch_nhtsa, fetch_usda
from backend.utils.fetch_fda_enforcement import (
    fetch_device_recalls,
    fetch_drug_recalls,
)
from backend.utils import db as db_utils
from backend.utils.alerts import create_alerts_for_new_recalls
from backend.tasks import send_alert, send_notifications
from backend.utils.ai_summary import summarize_recall


def refresh_recalls() -> Dict[str, int]:
    """Fetch latest recalls and upsert into the database."""
    conn = db_utils.connect()
    trans = conn.begin()
    new = 0
    updated = 0
    new_recall_rows: List[Dict] = []

    recalls: List[Dict] = []
    for func in (fetch_cpsc, fetch_fda, fetch_nhtsa, fetch_usda):
        recalls.extend(func(use_cache=False))
    recalls.extend(fetch_drug_recalls())
    recalls.extend(fetch_device_recalls())

    for r in recalls:
        existing = conn.execute(
            text("SELECT hazard FROM recalls WHERE id=:id AND source=:source"),
            {"id": r.get("id"), "source": r.get("source")},
        ).fetchone()

        summary, next_step = summarize_recall(
            r.get("product", ""), r.get("hazard", ""), r.get("classification")
        )

        params = {
            "id": r.get("id"),
            "product": r.get("product"),
            "hazard": r.get("hazard"),
            "date": r.get("recall_date"),
            "source": r.get("source"),
            "f": datetime.utcnow().isoformat(),
            "summary": summary,
            "next": next_step,
            "updates": "[]",
        }

        if existing:
            conn.execute(
                text(
                    "UPDATE recalls SET product=:product, hazard=:hazard, recall_date=:date, fetched_at=:f, summary_text=:summary, next_steps=:next WHERE id=:id AND source=:source"
                ),
                params,
            )
            updated += 1
        else:
            conn.execute(
                text(
                    "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at, summary_text, next_steps, remedy_updates) VALUES (:id, :product, :hazard, :date, :source, :f, :summary, :next, :updates)"
                ),
                params,
            )
            new += 1
            new_recall_rows.append(r)
    trans.commit()
    alert_ids = create_alerts_for_new_recalls(conn, recalls)
    if os.getenv("CELERY_BROKER_URL"):
        for aid in alert_ids:
            send_alert.delay(aid)
        if new_recall_rows:
            send_notifications.delay(new_recall_rows)
    else:
        for aid in alert_ids:
            send_alert(aid)
        if new_recall_rows:
            send_notifications(new_recall_rows)
    alerts_created = len(alert_ids)
    total = conn.execute(text("SELECT COUNT(*) FROM recalls")).fetchone()[0]
    conn.close()

    summary = {"new": new, "updated": updated, "total": total, "alerts": alerts_created}
    print(summary)
    return summary
