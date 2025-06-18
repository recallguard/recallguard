from flask import Blueprint, jsonify, request
from sqlalchemy import text
from backend.utils.auth import jwt_required, get_jwt_subject
from backend.utils.session import SessionLocal
from backend.db.models import user_items

bp = Blueprint("items", __name__)


def lookup_upc(db, upc: str) -> dict:
    info = db.execute(text("PRAGMA table_info(recalls)")).fetchall()
    cols = {r[1] for r in info}
    query = "SELECT id, product, hazard, remedy_updates"
    query += ", url" if "url" in cols else ", '' as url"
    query += " FROM recalls WHERE product=:p"
    params = {"p": upc}
    if "details" in cols:
        query += " OR json_extract(details, '$.upc')=:p"
    row = db.execute(text(query), params).fetchone()
    if row:
        m = row._mapping
        return {
            "status": "recalled",
            "recall_id": m["id"],
            "product_name": m["product"],
            "hazard": m["hazard"],
            "url": m["url"],
            "update_count": len(m["remedy_updates"] or []),
        }
    return {"status": "safe"}


@bp.get("/api/items")
@jwt_required
def list_items():
    user_id = get_jwt_subject()["user_id"]
    with SessionLocal() as db:
        rows = db.execute(
            user_items.select().where(user_items.c.user_id == user_id)
        ).fetchall()
        items = []
        for r in rows:
            item = dict(r._mapping)
            status = lookup_upc(db, item["upc"])
            item["status"] = status["status"]
            if "update_count" in status:
                item["update_count"] = status["update_count"]
            items.append(item)
        return jsonify(items)


@bp.post("/api/items")
@jwt_required
def add_item():
    data = request.get_json(force=True)
    upc = data.get("upc")
    if not upc:
        return jsonify({"error": "upc required"}), 400
    label = data.get("label")
    profile = data.get("profile") or "self"
    user_id = get_jwt_subject()["user_id"]
    with SessionLocal() as db:
        res = db.execute(
            user_items.insert().values(
                user_id=user_id, upc=upc, label=label, profile=profile
            )
        )
        db.commit()
        return jsonify({"id": res.lastrowid}), 201


@bp.delete("/api/items/<int:item_id>")
@jwt_required
def delete_item(item_id: int):
    user_id = get_jwt_subject()["user_id"]
    with SessionLocal() as db:
        db.execute(
            user_items.delete().where(
                user_items.c.id == item_id, user_items.c.user_id == user_id
            )
        )
        db.commit()
        return jsonify({"status": "ok"})
