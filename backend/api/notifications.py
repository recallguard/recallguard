from __future__ import annotations

import json
from datetime import datetime
from flask import Blueprint, Response, stream_with_context, jsonify, request
from sqlalchemy import text
from queue import Queue

from backend.utils.session import SessionLocal
from backend.db.models import alerts, subscriptions, push_tokens, email_unsub_tokens
from backend.utils.auth import jwt_required, get_jwt_subject

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


@bp.post('/api/subscriptions/')
@jwt_required
def create_subscription():
    data = request.get_json(force=True)
    recall_source = data.get('recall_source')
    product_query = data.get('product_query')
    user_id = get_jwt_subject()['user_id']
    with SessionLocal() as db:
        row = db.execute(
            subscriptions.insert().values(user_id=user_id, recall_source=recall_source, product_query=product_query)
        )
        db.commit()
        return jsonify({'id': row.lastrowid})


@bp.get('/api/subscriptions/')
@jwt_required
def list_subscriptions():
    user_id = get_jwt_subject()['user_id']
    with SessionLocal() as db:
        rows = db.execute(subscriptions.select().where(subscriptions.c.user_id == user_id)).fetchall()
        return jsonify([dict(r._mapping) for r in rows])


@bp.delete('/api/subscriptions/<int:sid>')
@jwt_required
def delete_subscription(sid: int):
    user_id = get_jwt_subject()['user_id']
    with SessionLocal() as db:
        db.execute(
            subscriptions.delete().where(subscriptions.c.id == sid, subscriptions.c.user_id == user_id)
        )
        db.commit()
    return jsonify({'status': 'ok'})


@bp.post('/api/email-opt-in')
@jwt_required
def email_opt_in():
    user_id = get_jwt_subject()['user_id']
    data = request.get_json(force=True)
    value = 1 if data.get('enabled') else 0
    with SessionLocal() as db:
        db.execute(
            text('UPDATE users SET email_opt_in=:v WHERE id=:u'),
            {'v': value, 'u': user_id},
        )
        db.commit()
    return jsonify({'status': 'ok'})


@bp.post('/api/push/register')
@jwt_required
def register_push() -> tuple:
    user_id = get_jwt_subject()['user_id']
    data = request.get_json(force=True)
    token = data.get('token')
    if not token:
        return jsonify({'error': 'missing token'}), 400
    with SessionLocal() as db:
        exists = db.execute(
            push_tokens.select().where(push_tokens.c.user_id == user_id, push_tokens.c.token == token)
        ).fetchone()
        if not exists:
            db.execute(push_tokens.insert().values(user_id=user_id, token=token))
            db.commit()
    return jsonify({'status': 'ok'})


@bp.delete('/api/push/<token>')
@jwt_required
def delete_push(token: str) -> tuple:
    user_id = get_jwt_subject()['user_id']
    with SessionLocal() as db:
        db.execute(
            push_tokens.delete().where(push_tokens.c.user_id == user_id, push_tokens.c.token == token)
        )
        db.commit()
    return jsonify({'status': 'ok'})


@bp.get('/api/unsubscribe/<token>')
def unsubscribe(token: str):
    with SessionLocal() as db:
        row = db.execute(email_unsub_tokens.select().where(email_unsub_tokens.c.token == token)).fetchone()
        if not row:
            return 'Invalid token', 404
        user_id = row._mapping['user_id']
        db.execute(text('UPDATE users SET email_opt_in=0 WHERE id=:u'), {'u': user_id})
        db.commit()
    return Response("You're unsubscribed", mimetype='text/html')
