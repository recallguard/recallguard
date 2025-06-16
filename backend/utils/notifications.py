from __future__ import annotations

from typing import List
from sqlalchemy import text
from os import getenv
import requests
from backend.utils.session import SessionLocal
from backend.db.models import sent_notifications, alerts


def match_subscriptions(db, recall: dict) -> List[dict]:
    query = text(
        "SELECT s.user_id, s.product_query FROM subscriptions s "
        "JOIN users u ON s.user_id=u.id "
        "WHERE s.recall_source=:src AND lower(:prod) LIKE '%' || lower(s.product_query) || '%' "
        "AND u.email_opt_in=1"
    )
    rows = db.execute(query, {"src": recall.get("source"), "prod": recall.get("product")}).fetchall()
    return [dict(r._mapping) for r in rows]


def queue_notifications(db, recall: dict) -> int:
    matches = match_subscriptions(db, recall)
    sent = 0
    for m in matches:
        with SessionLocal() as session:
            exists = session.execute(
                text("SELECT 1 FROM sent_notifications WHERE user_id=:u AND recall_id=:r"),
                {"u": m["user_id"], "r": recall.get("id")},
            ).fetchone()
            if exists:
                continue
            session.execute(
                sent_notifications.insert().values(user_id=m["user_id"], recall_id=recall.get("id"))
            )
            res = session.execute(
                alerts.insert().values(user_id=m["user_id"], recall_id=recall.get("id"), channel="email")
            )
            session.commit()
            slack = getenv("SLACK_WEBHOOK_URL")
            if slack:
                try:
                    requests.post(
                        slack,
                        json={
                            "text": f"\ud83d\udea8 *{recall['source'].upper()}* recall: *{recall['product']}* <{recall.get('url','')}|Read more>"
                        },
                    )
                except Exception:
                    pass
            if getenv("CELERY_BROKER_URL"):
                from backend.tasks import send_alert
                send_alert.delay(res.lastrowid)
            sent += 1
        SessionLocal.remove()
    return sent
