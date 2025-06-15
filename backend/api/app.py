from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request

from .recalls import fetch_all
from .alerts import check_user_items, generate_summary
from backend.db import init_db
from backend.utils.config import get_db_path
from backend.utils import db as db_utils

# simple in-memory store for user items
USER_ITEMS = []


def create_app() -> Flask:
    app = Flask(__name__)
    db_path = Path(get_db_path())
    init_db(db_path)

    @app.get('/recalls')
    def recalls_route():
        return jsonify(fetch_all())

    @app.post('/user-items')
    def add_item():
        data = request.get_json(force=True)
        item = data.get('item')
        if item:
            USER_ITEMS.append(item)
        return jsonify({'items': USER_ITEMS})

    @app.get('/alerts')
    def alerts_route():
        recalls = fetch_all()
        matches = check_user_items.check_user_items(USER_ITEMS, recalls)
        summaries = [generate_summary.generate_summary({'title': 'Recall', 'product': m}) for m in matches]
        return jsonify({'alerts': summaries})

    @app.get('/api/recalls/recent')
    def recent_recalls() -> tuple:
        conn = db_utils.connect(db_path)
        rows = conn.execute(
            'SELECT id, product, hazard, recall_date, source '
            'FROM recalls ORDER BY recall_date DESC LIMIT 25'
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

    @app.get('/api/recalls/user/<int:user_id>')
    def user_recalls(user_id: int) -> tuple:
        conn = db_utils.connect(db_path)
        rows = conn.execute(
            'SELECT r.id, r.product, r.hazard, r.recall_date, r.source '
            'FROM recalls r JOIN products p ON lower(r.product)=lower(p.name) '
            'WHERE p.user_id=? ORDER BY r.recall_date DESC',
            (user_id,),
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

    return app
