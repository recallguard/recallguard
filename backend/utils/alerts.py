from __future__ import annotations

from typing import List

from sqlalchemy import text

from backend.db.models import alerts


def create_alerts_for_new_recalls(db, new_recalls: List[dict]) -> list[int]:
    """Insert Alert rows for users impacted by new recalls."""
    alert_ids: list[int] = []
    for r in new_recalls:
        matched_users = db.execute(
            text("SELECT DISTINCT user_id FROM products WHERE lower(name)=lower(:p)"),
            {"p": r.get("product")},
        ).fetchall()
        for u in matched_users:
            res = db.execute(
                alerts.insert().values(
                    user_id=u._mapping["user_id"],
                    recall_id=r.get("id"),
                    channel="email",
                )
            )
            alert_ids.append(res.lastrowid)
    return alert_ids
