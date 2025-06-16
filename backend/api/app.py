from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, request

from .recalls import fetch_all
from backend.utils.refresh import refresh_recalls
from .alerts import check_user_items, generate_summary
from backend.db import init_db
from backend.utils.config import get_db_path
from backend.utils import db as db_utils

from backend.utils.auth import (
    create_access_token,
    hash_password,
    verify_password,
    jwt_required,
)
from datetime import datetime
import sqlite3



# simple in-memory store for user items
USER_ITEMS = []


def create_app() -> Flask:
    app = Flask(__name__)
    db_path = Path(get_db_path())
    init_db(db_path)

    app.config["DB_PATH"] = db_path

    @app.post('/api/auth/signup')
    def signup() -> tuple:
        data = request.get_json(force=True)
        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({'error': 'invalid'}), 400
        conn = db_utils.connect(db_path)
        try:
            cur = conn.execute(
                'INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)',
                (email, hash_password(password), datetime.utcnow().isoformat()),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'email exists'}), 400
        user_id = cur.lastrowid
        conn.close()
        token = create_access_token({'user_id': user_id})
        return jsonify({'token': token, 'user_id': user_id}), 201

    @app.post('/api/auth/login')
    def login() -> tuple:
        data = request.get_json(force=True)
        email = data.get('email')
        password = data.get('password')
        conn = db_utils.connect(db_path)
        row = conn.execute(
            'SELECT id, password_hash FROM users WHERE email=?', (email,)
        ).fetchone()
        conn.close()
        if not row or not verify_password(password, row['password_hash']):
            return jsonify({'error': 'invalid credentials'}), 401
        token = create_access_token({'user_id': row['id']})
        return jsonify({'token': token, 'user_id': row['id']})


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

    @jwt_required

    def recent_recalls() -> tuple:
        conn = db_utils.connect(db_path)
        rows = conn.execute(
            'SELECT id, product, hazard, recall_date, source '
            'FROM recalls ORDER BY recall_date DESC LIMIT 25'
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in rows])

    @app.get('/api/recalls/user/<int:user_id>')

    @jwt_required

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


    @app.post('/api/recalls/refresh')
    @jwt_required
    def manual_refresh() -> tuple:
        if request.headers.get('X-Admin') != 'true':
            return jsonify({'error': 'unauthorized'}), 403
        summary = refresh_recalls(db_path)
        return jsonify(summary)


    return app
