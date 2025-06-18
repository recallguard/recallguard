from __future__ import annotations

import os
from datetime import datetime

from celery import Celery
from backend.utils.email_utils import send_email
from urllib.parse import quote

from backend.utils.session import SessionLocal
from backend.db.models import (
    alerts,
    email_unsub_tokens,
    recalls,
    push_tokens,
    channel_subs,
    webhooks,
)
from backend.api.notifications import listeners
from backend.utils.notifications import queue_notifications
from sqlalchemy import text
import requests
import json
from slack_sdk import WebClient

SLACK_URL = os.getenv("SLACK_WEBHOOK_URL")
SLACK_TOKEN = os.getenv("SLACK_BOT_TOKEN")
slack_client = WebClient(token=SLACK_TOKEN) if SLACK_TOKEN else None

celery = Celery(
    "tasks", broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
)


def _send_push(db, user_id: int, message: str) -> None:
    tokens = db.execute(
        push_tokens.select().where(push_tokens.c.user_id == user_id)
    ).fetchall()
    for t in tokens:
        print("push", t._mapping["token"], message)


@celery.task(
    autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3}
)
def send_alert(alert_id: int, subject: str | None = None) -> None:
    with SessionLocal() as db:
        row = db.execute(alerts.select().where(alerts.c.id == alert_id)).fetchone()
        if not row:
            return
        mapping = row._mapping
        user_row = db.execute(
            text("SELECT email FROM users WHERE id=:u"), {"u": mapping["user_id"]}
        ).fetchone()
        email = user_row._mapping["email"] if user_row else None
        recall_row = db.execute(
            recalls.select().where(recalls.c.id == mapping["recall_id"])
        ).fetchone()
        summary = recall_row._mapping.get("summary_text") if recall_row else ""
        steps = recall_row._mapping.get("next_steps") if recall_row else ""
        # ensure an unsubscribe token exists
        token_row = db.execute(
            text("SELECT token FROM email_unsub_tokens WHERE user_id=:u"),
            {"u": mapping["user_id"]},
        ).fetchone()
        if not token_row:
            import secrets

            token = secrets.token_urlsafe(16)
            db.execute(
                email_unsub_tokens.insert().values(
                    user_id=mapping["user_id"], token=token
                )
            )
            unsub_token = token
        else:
            unsub_token = token_row._mapping["token"]
        base_url = os.getenv("BASE_URL", "")
        share_url = f"{os.getenv('FRONTEND_ORIGIN', '')}/signup?src=share"
        text_copy = (
            f"Recall alert: {recall_row._mapping.get('product')} – stay safe with RecallHero"
        )
        context = {
            "share_twitter": f"https://twitter.com/intent/tweet?text={quote(text_copy)}&url={quote(share_url)}",
            "share_facebook": f"https://www.facebook.com/sharer/sharer.php?u={quote(share_url)}&quote={quote(text_copy)}",
        }
        send_email(
            email,
            subject or "Recall Alert",
            "recall_alert.html",
            context,
        )
        db.execute(
            alerts.update()
            .where(alerts.c.id == alert_id)
            .values(sent_at=datetime.utcnow().isoformat())
        )
        db.commit()
    for q in listeners:
        q.put({"type": "new_alert"})


@celery.task(
    autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3}
)
def send_notifications(new_recalls: list[dict]) -> int:
    sent = 0
    db = SessionLocal()
    try:
        for recall in new_recalls:
            sent += queue_notifications(db, recall)
            if SLACK_URL:
                try:
                    requests.post(
                        SLACK_URL,
                        json={
                            "text": f"\ud83d\udea8 *{recall['source'].upper()}* recall: *{recall['product']}* <{recall.get('url','')}|Read more>"
                        },
                    )
                except Exception:
                    pass
            # channel subscriptions via Slack bot
            if slack_client:
                rows = db.execute(
                    channel_subs.select().where(
                        channel_subs.c.platform == "slack",
                        channel_subs.c.source == recall.get("source").upper(),
                    )
                ).fetchall()
                for r in rows:
                    if r._mapping["query"].lower() not in recall.get("product", "").lower():
                        continue
                    try:
                        slack_client.chat_postMessage(
                            channel=r._mapping["channel_id"],
                            text=f"*:rotating_light: {recall['source'].upper()} recall:* {recall['product']}"
                        )
                    except Exception:
                        pass
            # partner webhooks
            hooks = db.execute(
                webhooks.select().where(
                    (webhooks.c.source.is_(None)) | (webhooks.c.source == recall.get("source"))
                )
            ).fetchall()
            for wh in hooks:
                q = wh._mapping["query"]
                if q and q.lower() not in recall.get("product", "").lower():
                    continue
                try:
                    requests.post(wh._mapping["url"], json=recall, timeout=5)
                except Exception:
                    pass
    finally:
        db.close()
        SessionLocal.remove()
    return sent


@celery.task
def check_user_items_and_alert() -> None:
    """Placeholder daily scan of UserItem rows."""
    from backend.db.models import user_items

    with SessionLocal() as db:
        rows = db.execute(user_items.select()).fetchall()
        for r in rows:
            upc = r._mapping["upc"]
            status = db.execute(
                text("SELECT 1 FROM recalls WHERE product=:p"), {"p": upc}
            ).fetchone()
            if status:
                # In a real task we'd queue an alert
                print(f"Alert user {r._mapping['user_id']} UPC {upc} recalled")


@celery.task
def poll_remedy_updates() -> None:
    """Check for remedy updates on recalls."""
    from datetime import timedelta
    from backend.utils.remedy import extract_remedy

    with SessionLocal() as db:
        info = db.execute(text("PRAGMA table_info(recalls)")).fetchall()
        cols = {r[1] for r in info}
        has_url = "url" in cols
        query = "SELECT id, source, product, fetched_at, remedy_updates"
        if has_url:
            query += ", url"
        query += " FROM recalls WHERE source IN ('cpsc','nhtsa')"
        rows = db.execute(text(query)).fetchall()
        now = datetime.utcnow()
        for r in rows:
            m = r._mapping
            raw = m["remedy_updates"]
            updates = raw if isinstance(raw, list) else json.loads(raw or "[]")
            last = (
                datetime.fromisoformat(updates[-1]["time"])
                if updates
                else datetime.fromisoformat(m["fetched_at"])
            )
            if now - last < timedelta(hours=24):
                continue
            url = m.get("url")
            if not url:
                continue
            try:
                html = requests.get(url, timeout=10).text
            except Exception:
                continue
            remedy = extract_remedy(html)
            if not remedy:
                continue
            if updates and updates[-1]["text"].strip() == remedy.strip():
                continue
            updates.append({"time": now.isoformat(), "text": remedy.strip()})
            db.execute(
                recalls.update()
                .where(recalls.c.id == m["id"], recalls.c.source == m["source"])
                .values(remedy_updates=updates)
            )
            db.commit()
            users = db.execute(
                text(
                    "SELECT DISTINCT user_id FROM sent_notifications WHERE recall_id=:r"
                ),
                {"r": m["id"]},
            ).fetchall()
            message = f"Update on recall {m['product']}"
            for u in users:
                _send_push(db, u._mapping["user_id"], message)
                res = db.execute(
                    alerts.insert().values(
                        user_id=u._mapping["user_id"],
                        recall_id=m["id"],
                        channel="email",
                    )
                )
                subj = f"Update: {m['product']} recall"
                if os.getenv("CELERY_BROKER_URL"):
                    send_alert.delay(res.lastrowid, subj)
                else:
                    send_alert(res.lastrowid, subj)


@celery.task
def reset_monthly_quotas() -> None:
    """Reset API quotas based on plan at the start of each month."""
    with SessionLocal() as db:
        db.execute(
            text(
                "UPDATE stripe_customers SET quota = CASE plan WHEN 'free' THEN 100 WHEN 'pro' THEN 10000 ELSE quota END"
            )
        )
        db.commit()
