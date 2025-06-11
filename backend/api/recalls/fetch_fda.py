"""backend/api/recalls/fetch_fda.py
=================================
Fetch **Food & Drug Administration (FDA)** enforcement‐action recalls and
persist only *new* items into the ``recalls`` table.

openFDA exposes JSON endpoints for *food*, *drug* and *device* enforcement
reports.  We poll each endpoint in reverse chronological order and stop as
soon as we encounter either of the following:

* a ``recall_number`` we already have in the database
* a ``report_date`` older than the configurable ``cutoff_days`` window

The task is scheduled via :pyfunc:`backend.utils.scheduler.get_scheduler`.
See the constants at the top for default poll frequency & cutoff window.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import logging
from typing import Any, Dict, List

import httpx
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Recall, RecallSource
from backend.utils.config import get_settings
from backend.utils.logging import setup_logging
from backend.utils.scheduler import get_scheduler

__all__ = ["fetch_fda", "register_job"]

logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
OPENFDA_BASE = "https://api.fda.gov/{category}/enforcement.json"
DEFAULT_LIMIT = 100  # max = 1000 but staying polite to avoid 429s
CATEGORIES = ("food", "drug", "device")
POLL_MINUTES = 60  # how often APScheduler should run this task
CUTOFF_DAYS = 14   # ignore recalls older than this window

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_date(date_str: str) -> dt.date | None:
    """Convert YYYYMMDD strings to :class:`datetime.date`."""
    try:
        return dt.datetime.strptime(date_str, "%Y%m%d").date()
    except (TypeError, ValueError):
        return None


def _normalise(record: Dict[str, Any]) -> Dict[str, Any]:
    """Map the openFDA payload into our Recall ORM schema."""
    report_date = _parse_date(record.get("report_date"))
    recall_number: str = record.get("recall_number", "").strip()

    return {
        "recall_id": recall_number,
        "source": RecallSource.FDA.value,
        "title": record.get("product_description", "").strip()[:255],
        "description": record.get("reason_for_recall", "").strip(),
        "hazard": record.get("classification", "").strip(),
        "url": record.get("more_code_info", "").strip() or record.get("web_link", "").strip(),
        "affected_units": None,
        "recall_date": report_date or dt.date.today(),
        "raw_payload": record,  # keep entire JSON for debugging
    }


async def _fetch_page(client: httpx.AsyncClient, category: str, skip: int) -> List[Dict[str, Any]]:
    """Fetch one page (``limit`` rows) from the openFDA endpoint."""
    search = "status:O"  # open recalls; historical too but keeps size reasonable
    params = {
        "search": search,
        "sort": "report_date:desc",
        "limit": DEFAULT_LIMIT,
        "skip": skip,
    }
    url = OPENFDA_BASE.format(category=category)
    resp = await client.get(url, params=params, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    return data.get("results", [])


async def _bulk_insert(session: AsyncSession, payloads: List[Dict[str, Any]]) -> int:
    """Insert recalls ignoring duplicates. Returns number of new rows."""
    if not payloads:
        return 0
    try:
        await session.execute(
            Recall.__table__.insert()
            .prefix_with("OR IGNORE" if session.bind.dialect.name == "sqlite" else "ON CONFLICT DO NOTHING"),
            payloads,
        )
        await session.commit()
        return len(payloads)
    except SQLAlchemyError as exc:
        await session.rollback()
        logger.error("FDA fetch – DB insert failed: %s", exc, exc_info=True)
        return 0


# ---------------------------------------------------------------------------
# Main entry‑point
# ---------------------------------------------------------------------------

async def fetch_fda(session: AsyncSession, *, cutoff_days: int = CUTOFF_DAYS) -> int:
    """Poll the FDA enforcement APIs and store *new* recalls.

    Returns the number of new rows inserted.
    """
    logger.info("Fetching FDA recalls (window=%sd)…", cutoff_days)
    earliest_allowed = dt.date.today() - dt.timedelta(days=cutoff_days)
    new_rows = 0

    async with httpx.AsyncClient(headers={"User-Agent": "RecallGuard/1.0"}, follow_redirects=True) as client:
        for category in CATEGORIES:
            logger.debug("Polling category=%s", category)
            skip = 0
            done = False

            while not done:
                try:
                    records = await _fetch_page(client, category, skip)
                except httpx.HTTPStatusError as exc:
                    # 429 or 5xx – backoff
                    logger.warning("openFDA %s HTTP error: %s", category, exc)
                    await asyncio.sleep(5)
                    continue
                if not records:
                    break

                # Fetch existing recall_ids so we can early‑abort if we see one
                recall_ids = [r.get("recall_number") for r in records if r.get("recall_number")]
                existing = set()
                if recall_ids:
                    q = select(Recall.recall_id).where(Recall.recall_id.in_(recall_ids))
                    res = await session.execute(q)
                    existing = {row[0] for row in res.all()}

                payload_batch: List[Dict[str, Any]] = []
                for rec in records:
                    rec_id = rec.get("recall_number")
                    if not rec_id or rec_id in existing:
                        done = True
                        continue
                    report_date = _parse_date(rec.get("report_date"))
                    if report_date and report_date < earliest_allowed:
                        done = True
                        continue
                    payload_batch.append(_normalise(rec))

                inserted = await _bulk_insert(session, payload_batch)
                new_rows += inserted

                skip += DEFAULT_LIMIT

    logger.info("FDA fetch complete – %s new recalls", new_rows)
    return new_rows


# ---------------------------------------------------------------------------
# Scheduler hook
# ---------------------------------------------------------------------------

def register_job() -> None:
    """Register the task with the global APScheduler instance."""
    scheduler = get_scheduler()
    scheduler.add_job(
        fetch_fda,
        "interval",
        minutes=POLL_MINUTES,
        id="fetch_fda_recalls",
        max_instances=1,
        coalesce=True,
        kwargs={"cutoff_days": CUTOFF_DAYS},
    )
    logger.info("Registered APScheduler job: fetch_fda_recalls every %s min(s)", POLL_MINUTES)


# Ensure logging is configured when module is imported during standalone runs
setup_logging()
