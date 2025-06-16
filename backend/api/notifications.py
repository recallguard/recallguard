from __future__ import annotations

import json
from datetime import datetime
from flask import Blueprint, Response, stream_with_context, jsonify
from queue import Queue

from backend.utils.session import SessionLocal
from backend.db.models import alerts

bp = Blueprint('alerts', __name__)
listeners: list[Queue] = []

@bp.route('/ws/alerts')
def alerts_ws():
    q: Queue = Queue()
    listeners.append(q)

    def gen():
        while True:
            data = q.get()
            yield f"data: {json.dumps(data)}\n\n"
    return Response(stream_with_context(gen()), mimetype='text/event-stream')

@bp.route('/api/alerts')
def list_alerts():
    with SessionLocal() as db:
        rows = db.execute(alerts.select().limit(50)).fetchall()
        return jsonify([dict(r._mapping) for r in rows])

@bp.post('/api/alerts/<int:alert_id>/read')
def mark_read(alert_id: int):
    with SessionLocal() as db:
        db.execute(
            alerts.update().where(alerts.c.id == alert_id).values(read_at=datetime.utcnow().isoformat())
        )
        db.commit()
    return jsonify({'status': 'ok'})
