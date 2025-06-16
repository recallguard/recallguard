from __future__ import annotations

import os
from datetime import datetime

from celery import Celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from backend.utils.session import SessionLocal
from backend.db.models import alerts
from backend.api.notifications import listeners

celery = Celery('tasks', broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'))

@celery.task
def send_alert(alert_id: int) -> None:
    with SessionLocal() as db:
        row = db.execute(
            alerts.select().where(alerts.c.id == alert_id)
        ).fetchone()
        if not row:
            return
        mapping = row._mapping
        body = f"Recall {mapping['recall_id']}"  # simple message
        api_key = os.getenv('SENDGRID_API_KEY')
        if api_key:
            message = Mail(
                from_email=os.getenv('ALERTS_FROM_EMAIL', 'noreply@example.com'),
                to_emails=mapping['user_id'],
                subject='Recall Alert',
                plain_text_content=body,
            )
            try:
                sg = SendGridAPIClient(api_key)
                sg.send(message)
                db.execute(
                    alerts.update().where(alerts.c.id == alert_id).values(sent_at=datetime.utcnow().isoformat())
                )
            except Exception as e:
                db.execute(
                    alerts.update().where(alerts.c.id == alert_id).values(error=str(e))
                )
        else:
            print('send alert', alert_id, body)
            db.execute(
                alerts.update().where(alerts.c.id == alert_id).values(sent_at=datetime.utcnow().isoformat())
            )
        db.commit()
    for q in listeners:
        q.put({'type': 'new_alert'})
