from flask import Blueprint, request, jsonify
from backend.utils.auth import jwt_required, get_jwt_subject
from backend.utils.session import SessionLocal
from backend.db.models import stripe_customers
import os
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

bp = Blueprint("billing", __name__)


@bp.post("/api/billing/checkout")
@jwt_required
def create_checkout():
    data = request.get_json(force=True)
    plan = data.get("plan")
    seats = int(data.get("seats", 1))
    if plan not in ("pro", "enterprise"):
        return jsonify({"error": "invalid plan"}), 400
    lookup = {
        "pro": "pro-monthly",
        "enterprise": "enterprise-seat",
    }
    session = stripe.checkout.Session.create(
        mode="subscription",
        success_url=f"{os.getenv('FRONTEND_ORIGIN','')}/settings/billing?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{os.getenv('FRONTEND_ORIGIN','')}/settings/billing",
        line_items=[{"price": lookup[plan], "quantity": seats}],
        metadata={"user_id": get_jwt_subject()["user_id"], "plan": plan, "seats": seats},
    )
    return jsonify({"url": session.url})


@bp.post("/api/billing/portal")
@jwt_required
def billing_portal():
    uid = get_jwt_subject()["user_id"]
    with SessionLocal() as db:
        row = db.execute(
            stripe_customers.select().where(stripe_customers.c.user_id == uid)
        ).fetchone()
        if not row or not row._mapping.get("stripe_customer_id"):
            return jsonify({"error": "not found"}), 404
        portal = stripe.billing_portal.Session.create(
            customer=row._mapping["stripe_customer_id"],
            return_url=f"{os.getenv('FRONTEND_ORIGIN','')}/settings/billing",
        )
        return jsonify({"url": portal.url})


@bp.post("/api/stripe/webhook")
def webhook():
    event = request.get_json(force=True)
    typ = event.get("type")
    obj = event.get("data", {}).get("object", {})
    uid = obj.get("metadata", {}).get("user_id")
    plan = obj.get("metadata", {}).get("plan")
    seats = int(obj.get("metadata", {}).get("seats", 1))
    if typ in ("checkout.session.completed", "customer.subscription.updated"):
        with SessionLocal() as db:
            row = db.execute(
                stripe_customers.select().where(stripe_customers.c.user_id == uid)
            ).fetchone()
            values = {
                "plan": plan or row._mapping.get("plan", "free"),
                "seats": seats,
                "stripe_customer_id": obj.get("customer") or row and row._mapping.get("stripe_customer_id"),
                "subscription_id": obj.get("subscription") or obj.get("id"),
                "quota": 10000 if (plan or row._mapping.get("plan")) == "pro" else None,
            }
            if row:
                db.execute(
                    stripe_customers.update().where(stripe_customers.c.user_id == uid).values(**values)
                )
            else:
                values["user_id"] = uid
                if values["quota"] is None and (plan or "") != "enterprise":
                    values["quota"] = 100
                db.execute(stripe_customers.insert().values(**values))
            db.commit()
    elif typ == "customer.subscription.deleted":
        with SessionLocal() as db:
            db.execute(
                stripe_customers.update()
                .where(stripe_customers.c.user_id == uid)
                .values(plan="free", quota=100)
            )
            db.commit()
    return "", 200
