"""Data refresh utilities."""
from __future__ import annotations

from typing import Dict, List
from datetime import datetime


import os
from sqlalchemy import text

from backend.api.recalls import fetch_cpsc, fetch_fda, fetch_nhtsa, fetch_usda
from backend.utils import db as db_utils
from backend.utils.alerts import create_alerts_for_new_recalls
from backend.tasks import send_alert, send_notifications


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

    for r in recalls:
        existing = conn.execute(
            text("SELECT id FROM recalls WHERE id=:id AND source=:source"),
            {"id": r.get("id"), "source": r.get("source")},
        ).fetchone()
        if existing:
            conn.execute(

                text(
                    "UPDATE recalls SET product=:product, hazard=:hazard, recall_date=:date, fetched_at=:f WHERE id=:id AND source=:source"
                ),
                {
                    "product": r.get("product"),
                    "hazard": r.get("hazard"),
                    "date": r.get("recall_date"),
                    "f": datetime.utcnow().isoformat(),
                    "id": r.get("id"),
                    "source": r.get("source"),
                },

                "UPDATE recalls SET product=?, hazard=?, recall_date=?, fetched_at=? "
                "WHERE id=? AND source=?",
                (
                    r.get("product"),
                    r.get("hazard"),
                    r.get("recall_date"),
                    datetime.utcnow().isoformat(),
                    r.get("id"),
                    r.get("source"),
                ),

            )
            updated += 1
        else:
            conn.execute(

                text(
                    "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) VALUES (:id, :product, :hazard, :date, :source, :f)"
                ),
                {
                    "id": r.get("id"),
                    "product": r.get("product"),
                    "hazard": r.get("hazard"),
                    "date": r.get("recall_date"),
                    "source": r.get("source"),
                    "f": datetime.utcnow().isoformat(),
                },

                "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    r.get("id"),
                    r.get("product"),
                    r.get("hazard"),
                    r.get("recall_date"),
                    r.get("source"),
                    datetime.utcnow().isoformat(),
                ),

            )
            new += 1
            new_recall_rows.append(r)
    trans.commit()
    alert_ids = create_alerts_for_new_recalls(conn, recalls)
    if os.getenv('CELERY_BROKER_URL'):
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
