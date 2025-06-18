from __future__ import annotations

from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import text

from .ops import bp as ops_bp
from .notifications import bp as notifications_bp
from .items import bp as items_bp
from backend.utils.logging import configure_logging
from .recalls import fetch_all
from backend.utils.refresh import refresh_recalls
from backend.utils.nhtsa_vin import get_recalls_for_vin
from .alerts import check_user_items, generate_summary
from backend.db import init_db
from backend.utils import db as db_utils
from backend.utils.auth import (
    create_access_token,
    hash_password,
    verify_password,
    jwt_required,
)

# simple in-memory store for user items
USER_ITEMS: list[str] = []


def create_app() -> Flask:
    app = Flask(__name__)

    configure_logging()
    init_db()

    @app.post("/api/auth/signup")
    def signup() -> tuple:
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")
        if not email or not password:
            return jsonify({"error": "invalid"}), 400
        conn = db_utils.connect()
        try:
            cur = conn.execute(
                text(
                    "INSERT INTO users (email, password_hash, created_at) VALUES (:e, :p, :c)"
                ),
                {
                    "e": email,
                    "p": hash_password(password),
                    "c": datetime.utcnow().isoformat(),
                },
            )
            conn.commit()
        except Exception:
            conn.close()
            return jsonify({"error": "email exists"}), 400
        user_id = cur.lastrowid
        conn.close()
        token = create_access_token({"user_id": user_id})
        return jsonify({"token": token, "user_id": user_id}), 201

    @app.post("/api/auth/login")
    def login() -> tuple:
        data = request.get_json(force=True)
        email = data.get("email")
        password = data.get("password")
        conn = db_utils.connect()
        row = conn.execute(
            text("SELECT id, password_hash FROM users WHERE email=:e"), {"e": email}
        ).fetchone()
        conn.close()
        mapping = row._mapping if row is not None else None
        if not mapping or not verify_password(password, mapping["password_hash"]):
            return jsonify({"error": "invalid credentials"}), 401

        token = create_access_token({"user_id": mapping["id"]})
        return jsonify({"token": token, "user_id": mapping["id"]})

    @app.get("/recalls")
    def recalls_route():
        return jsonify(fetch_all())

    @app.post("/user-items")
    def add_item():
        data = request.get_json(force=True)
        item = data.get("item")
        if item:
            USER_ITEMS.append(item)
        return jsonify({"items": USER_ITEMS})

    @app.get("/alerts")
    def alerts_route():
        recalls = fetch_all()
        matches = check_user_items.check_user_items(USER_ITEMS, recalls)
        summaries = [
            generate_summary.generate_summary({"title": "Recall", "product": m})
            for m in matches
        ]
        return jsonify({"alerts": summaries})

    @app.get("/api/recalls/recent")
    @jwt_required
    def recent_recalls() -> tuple:
        conn = db_utils.connect()
        rows = conn.execute(
            text(
                "SELECT id, product, hazard, recall_date, source FROM recalls ORDER BY recall_date DESC LIMIT 25"
            )
        ).fetchall()
        conn.close()
        return jsonify([dict(row._mapping) for row in rows])

    @app.get("/api/recalls/user/<int:user_id>")
    @jwt_required
    def user_recalls(user_id: int) -> tuple:
        conn = db_utils.connect()
        rows = conn.execute(
            text(
                "SELECT r.id, r.product, r.hazard, r.recall_date, r.source "
                "FROM recalls r JOIN products p ON lower(r.product)=lower(p.name) "
                "WHERE p.user_id=:u ORDER BY r.recall_date DESC"
            ),
            {"u": user_id},
        ).fetchall()
        conn.close()

        return jsonify([dict(row._mapping) for row in rows])

    @app.get("/api/recalls/vin/<vin>")
    @jwt_required
    def vin_recalls(vin: str):
        if len(vin) != 17 or not vin.isalnum():
            return jsonify({"error": "invalid VIN"}), 400
        recalls = get_recalls_for_vin(vin)
        return jsonify(recalls)


    @app.get("/api/check/<upc>")
    def check_upc(upc: str):
        if not upc.isdigit():
            return jsonify({"error": "invalid upc"}), 400
        conn = db_utils.connect()
        info = conn.execute(text("PRAGMA table_info(recalls)")).fetchall()
        cols = {r[1] for r in info}
        query = "SELECT id, product, hazard"
        query += ", url" if "url" in cols else ", '' as url"
        query += " FROM recalls WHERE product=:p"
        params = {"p": upc}
        if "details" in cols:
            query += " OR json_extract(details, '$.upc')=:p"
        row = conn.execute(text(query), params).fetchone()
        conn.close()
        if not row:
            return jsonify({"status": "safe"})
        m = row._mapping
        return jsonify(
            {
                "status": "recalled",
                "recall_id": m["id"],
                "product_name": m["product"],
                "hazard": m["hazard"],
                "url": m["url"],
            }
        )


    @app.post("/api/recalls/refresh")
    @jwt_required
    def manual_refresh() -> tuple:
        if request.headers.get("X-Admin") != "true":
            return jsonify({"error": "unauthorized"}), 403
        summary = refresh_recalls()
        return jsonify(summary)

    app.register_blueprint(ops_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(items_bp)

    return app
