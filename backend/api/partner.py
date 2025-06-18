from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import text
from backend.db.models import api_keys, webhooks, recalls
from backend.utils.session import SessionLocal

bp = Blueprint("partner", __name__)


def _get_api_key(db, key: str | None):
    if not key:
        return None
    row = db.execute(api_keys.select().where(api_keys.c.key == key)).fetchone()
    return row._mapping if row else None


@bp.get("/v1/recalls")
def list_recalls():
    key = request.headers.get("X-Api-Key")
    q = request.args.get("q", "")
    source = request.args.get("source")
    with SessionLocal() as db:
        record = _get_api_key(db, key)
        if not record:
            return jsonify({"error": "invalid key"}), 401
        if record["requests_this_month"] >= record["monthly_quota"]:
            return jsonify({"error": "quota exceeded"}), 429
        db.execute(
            api_keys.update()
            .where(api_keys.c.id == record["id"])
            .values(requests_this_month=record["requests_this_month"] + 1)
        )
        params = {}
        sql = "SELECT id, product, hazard, recall_date, source FROM recalls WHERE 1=1"
        if q:
            sql += " AND lower(product) LIKE '%' || lower(:q) || '%'"
            params["q"] = q
        if source:
            sql += " AND source=:src"
            params["src"] = source
        sql += " ORDER BY recall_date DESC LIMIT 50"
        rows = db.execute(text(sql), params).fetchall()
        db.commit()
        return jsonify([dict(r._mapping) for r in rows])


@bp.post("/v1/webhooks")
def create_webhook():
    key = request.headers.get("X-Api-Key")
    data = request.get_json(force=True)
    url = data.get("url")
    query = data.get("query")
    source = data.get("source")
    if not url:
        return jsonify({"error": "missing url"}), 400
    with SessionLocal() as db:
        record = _get_api_key(db, key)
        if not record:
            return jsonify({"error": "invalid key"}), 401
        res = db.execute(
            webhooks.insert().values(
                api_key_id=record["id"], url=url, query=query, source=source
            )
        )
        db.commit()
        return jsonify({"id": res.lastrowid})
