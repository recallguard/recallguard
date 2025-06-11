"""backend/main.py
=================
Entry‑point that assembles and exposes the FastAPI application.

Import this file with:
    uvicorn backend.main:app --reload
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.utils.config import get_settings
from backend.utils.logging import setup_logging
from backend.utils.logging import logging
from backend.utils.scheduler import get_scheduler

# Import your API sub‑modules / routers (adjust paths as needed)
from backend.api.users import auth, preferences
from backend.api.products import manual_entry, vin_lookup, email_import, vision_scan
from backend.api.recalls import fetch_cpsc, fetch_fda, fetch_nhtsa, fetch_usda, scrape_misc
from backend.api.alerts import check_user_items, generate_summary, send_email_alert

settings = get_settings()
log = logging.getLogger(__name__)

setup_logging()

def create_app() -> FastAPI:
    app = FastAPI(title="RecallGuard API", version="1.0.0")

    # ── CORS ───────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Routers ────────────────────────────────────────────────────────
    app.include_router(auth.router, prefix="/auth", tags=["Auth"])
    app.include_router(preferences.router, prefix="/preferences", tags=["Preferences"])

    app.include_router(manual_entry.router, prefix="/products", tags=["Products"])
    app.include_router(vin_lookup.router, prefix="/products", tags=["Products"])
    app.include_router(email_import.router, prefix="/products", tags=["Products"])
    app.include_router(vision_scan.router, prefix="/products", tags=["Products"])

    # Recalls fetchers (might expose via admin endpoints)
    # e.g., /admin/recalls/refresh

    # ── Scheduler jobs ────────────────────────────────────────────────
    scheduler = get_scheduler(app)
    check_user_items.register_job(scheduler)
    generate_summary.register_job(scheduler)
    send_email_alert.register_job(scheduler)

    return app


app = create_app()
