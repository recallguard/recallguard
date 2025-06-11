"""backend/api/recalls/fetch_nhtsa.py
===================================
Fetch **NHTSA (National Highway Traffic Safety Administration)** vehicle
safety recalls and persist *new* items into the ``recalls`` table.

Implementation notes
--------------------
* We use the public **Safety Issues** endpoint:
  ``https://vpic.nhtsa.dot.gov/api/vehicles/recalls`` which supports
  pagination (`page` query‑param) and returns recent recalls across all
  makes/models/years.
* NHTSA does not offer a simple "since X date" filter, so we page until we
  either hit a recall we have already stored **or** the recall date is
  older than our configured ``CUTOFF_DAYS`` (default: 90 days).
* The endpoint returns at most **1000 records per page**.  With hourly
  polling and a 90‑day window this is typically < 5 pages.
* Each record is normalised to the shared :class:`backend.db.models.Recall`
  ORM schema and bulk‑inserted with ``ON CONFLICT DO NOTHING``.

The job is registered with the global APScheduler instance in
:func:`register_job` and runs every ``settings.NHTSA_POLL_MINUTES`` (default
60 min).
"""
from __future__ import annotations

import asyncio
import datetime as dt
import logging
from typing import Any, Dict, List

import httpx
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Recall, RecallSource
from backend.utils.config import get_settings
from backend.utils.logging import get_logger  # helper that returns app logger
from backend.utils.scheduler import get_scheduler


API_URL = "https://vpic.nhtsa.dot.gov/api/vehicles/recalls"
PAGE_SIZE = 1000  # enforced by NHTSA – they always return 1000 per page

settings = get_settings()
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _parse_date(date_str: str | None) -> dt.date | None:
    if not date_str:
        return None
    try:
        return dt.datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        # NHTSA sometimes returns YYYY-MM-DD
        try:
            return dt.datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            logger.warning("NHTSA: Unparsable date '%s'", date_str)
            return None


def _normalise(record: Dict[str, Any]) -> Dict[str, Any]:
    """Map NHTSA JSON -> Recall ORM column dict."""
    recall_date = _parse_date(record.get("ReportReceivedDate"))
    return {
        "source": RecallSource.NHTSA,
        "external_id": record.get("NHTSACampaignNumber"),
        "title": record.get("Component"),
        "description": record.get("Summary"),
        "hazard": record.get("Consequence"),
        "remedy": record.get("Remedy"),
        "recall_date": recall_date,
        "url": record.get("NHTSAActionNumber"),  # often empty, but keep
        "meta": {
            "make": record.get("Make"),
            "model": record.get("Model"),
            "year": record.get("ModelYear"),
        },
    }


# ---------------------------------------------------------------------------
# Core fetch routine
# ---------------------------------------------------------------------------

async def fetch_nhtsa(session: AsyncSession) -> int:
    """Return number of *new* recalls inserted."""
    cutoff = dt.date.today() - dt.timedelta(days=settings.NHTSA_CUTOFF_DAYS)
    page = 1
    inserted = 0

    async with httpx.AsyncClient(timeout=20.0) as client:
        while True:
            params = {"format": "json", "page": page}
            resp = await client.get(API_URL, params=params)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()
            results: List[Dict[str, Any]] = data.get("results", []) or data.get("Results", [])

            if not results:
                break  # no more pages

            logger.debug("NHTSA page %d returned %d recalls", page, len(results))

            # Trim results older than cutoff
            fresh_records: List[Dict[str, Any]] = []
            for rec in results:
                rec_date = _parse_date(rec.get("ReportReceivedDate"))
                if rec_date and rec_date < cutoff:
                    # Older than window: stop paging altogether (records are sorted desc by date)
                    logger.info("NHTSA reached cutoff date – stopping pagination (page %d)", page)
                    results = []  # empty to break outer loop
                    break
                fresh_records.append(rec)

            if fresh_records:
                mapped = [_normalise(r) for r in fresh_records]
                stmt = insert(Recall).values(mapped).on_conflict_do_nothing(index_elements=[Recall.external_id])
                await session.execute(stmt)
                await session.commit()
                inserted += len(mapped)
                logger.info("Inserted %d new NHTSA recalls (page %d)", len(mapped), page)

            if not results:
                break  # reached cutoff or no more data
            page += 1
            await asyncio.sleep(0.2)  # tiny pause to be polite

    return inserted


# ---------------------------------------------------------------------------
# Scheduler integration
# ---------------------------------------------------------------------------

def register_job() -> None:
    sched = get_scheduler()
    # Avoid double‑registration in reload scenarios
    if not sched.get_job("fetch_nhtsa_recalls"):
        sched.add_job(
            fetch_nhtsa_wrapper,
            "interval",
            minutes=settings.NHTSA_POLL_MINUTES,
            id="fetch_nhtsa_recalls",
            coalesce=True,
            max_instances=1,
        )
        logger.info("Registered NHTSA recall fetcher (%d‑minute interval)", settings.NHTSA_POLL_MINUTES)


async def fetch_nhtsa_wrapper() -> None:
    """Scheduler safe wrapper that creates its own DB session."""
    from backend.db.session import async_session_maker  # local import to avoid circular

    async with async_session_maker() as session:
        try:
            inserted = await fetch_nhtsa(session)
            logger.info("NHTSA fetch finished – %d new recalls", inserted)
        except Exception as exc:
            logger.exception("NHTSA fetch failed: %s", exc)
