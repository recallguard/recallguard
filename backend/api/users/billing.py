"""backend/api/users/billing.py
================================
Subscription & payment management powered by **Stripe**.

The router exposes endpoints that let a logged‑in user:

* **POST /billing/portal‑link**   – receive a Stripe Billing Portal URL so
  they can update card details, view invoices, or cancel.
* **POST /billing/checkout‑session** – start a new Checkout Session for the
  selected price ID (upgrade from free tier).
* **GET  /billing/status**        – get current subscription status
  (plan, renewal date, trial, etc.).

Stripe webhooks are also handled at **/billing/webhook** and update the
local ``User.billing_status`` + ``User.stripe_customer_id`` fields in the
DB accordingly.

Notes
-----
* All client‑side Stripe keys come from ``settings.STRIPE_PUBLIC_KEY`` and
  ``settings.STRIPE_SECRET_KEY``.
* Webhooks require the signing secret (``STRIPE_WEBHOOK_SECRET``) and are
  verified with the official SDK.
* Only minimal error handling is included – extend as needed.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Annotated, Any, Generator

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.models import SessionLocal, User
from backend.utils.config import get_settings
from backend.api.users.auth import get_current_user

log = logging.getLogger(__name__)
settings = get_settings()

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/billing", tags=["billing"])

# ─────────────────────────────────────────────────────────────────────────────
# DB dependency helper
# ─────────────────────────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:  # noqa: D401 – FastAPI style
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ─────────────────────────────────────────────────────────────────────────────

class CheckoutSessionIn(BaseModel):
    price_id: str  # Stripe price ID to subscribe/purchase

class BillingStatusOut(BaseModel):
    plan: str | None
    current_period_end: datetime | None
    trial_end: datetime | None
    cancel_at_period_end: bool | None

# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/checkout-session", status_code=status.HTTP_201_CREATED)
async def create_checkout_session(
    payload: CheckoutSessionIn,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Create a Stripe Checkout Session so the user can subscribe/upgrade."""
    try:
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(email=current_user.email)
            current_user.stripe_customer_id = customer.id
            with SessionLocal() as db:
                db.add(current_user)
                db.commit()

        session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            mode="subscription",
            line_items=[{"price": payload.price_id, "quantity": 1}],
            success_url=f"{settings.FRONTEND_URL}/billing/success",
            cancel_url=f"{settings.FRONTEND_URL}/billing/cancel",
        )
        return {"checkout_url": session.url}
    except stripe.error.StripeError as exc:  # pragma: no cover
        log.error("Stripe error: %s", exc)
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/portal-link", status_code=status.HTTP_201_CREATED)
async def create_billing_portal_link(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Return a Stripe Billing Portal link so the user can manage payments."""
    if not current_user.stripe_customer_id:
        raise HTTPException(404, "Stripe customer not found – create a subscription first")

    session = stripe.billing_portal.Session.create(
        customer=current_user.stripe_customer_id,
        return_url=f"{settings.FRONTEND_URL}/account",
    )
    return {"portal_url": session.url}


@router.get("/status", response_model=BillingStatusOut)
async def get_billing_status(current_user: Annotated[User, Depends(get_current_user)]):
    """Return the current subscription state for the logged‑in user."""
    sub = None
    if current_user.stripe_subscription_id:
        sub = stripe.Subscription.retrieve(current_user.stripe_subscription_id)

    return BillingStatusOut(
        plan=sub["plan"]["nickname"] if sub else None,
        current_period_end=datetime.fromtimestamp(sub["current_period_end"]) if sub else None,
        trial_end=datetime.fromtimestamp(sub["trial_end"]) if sub and sub["trial_end"] else None,
        cancel_at_period_end=sub["cancel_at_period_end"] if sub else None,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Webhook handler
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    stripe_signature: Annotated[str, Header(alias="Stripe-Signature")],
):
    """Handle Stripe webhook events (subscription updates, invoice paid, …)."""
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=stripe_signature,
            secret=settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError as exc:  # Invalid payload
        log.warning("Invalid Stripe payload: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid payload") from exc
    except stripe.error.SignatureVerificationError as exc:  # Invalid signature
        log.warning("Invalid Stripe signature: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    event_type = event["type"]
    data: dict[str, Any] = event["data"]["object"]
    log.info("Stripe webhook: %s", event_type)

    with SessionLocal() as db:
        if event_type == "checkout.session.completed":
            customer_id = data.get("customer")
            subscription_id = data.get("subscription")
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.stripe_subscription_id = subscription_id
                user.billing_status = "active"
                db.commit()

        elif event_type == "customer.subscription.updated":
            sub_status = data["status"]
            customer_id = data["customer"]
            user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
            if user:
                user.billing_status = sub_status
                db.commit()

    return JSONResponse(status_code=200, content={"received": True})
