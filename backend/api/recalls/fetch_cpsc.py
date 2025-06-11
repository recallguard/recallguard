"""backend/api/recalls/fetch_cpsc.py
=================================
Fetch **Consumer Product Safety Commission (CPSC)** recalls and persist only
*new* records into the ``recalls`` table.

The CPSC exposes a convenient JSON feed that we page through every hour
(default).  The moment we hit a recall we already have **or** a record
older than ``cutoff_days`` we stop.  Everything else is normalised and
bulk‑inserted.

The module _must_ remain import‑side‑effect‑free so it can be safely
imported by Alembic migrations and unit‑tests.  The APScheduler job is
registered by explicitly calling :pyfunc:`register_job` at start‑up.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

import httpx
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Recall, RecallSource
from backend.utils.config import get_settings
from backend.utils.scheduler import get_scheduler

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CPSC_ENDPOINT = "https://www.saferproducts.gov/RestWebServices/Recall.json"
PAGE_SIZE = 100  # max allowed by the API

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------
async def fetch_cpsc(
    db: AsyncSession,
    *,
    http_client: Optional[httpx.AsyncClient] = None,
    cutoff_days: int | None = None,
) -> int:
    """Poll the CPSC feed and insert new recalls.

    Parameters
    ----------
    db:
        An *active* ``AsyncSession`` instance.
    http_client:
        Re‑use an existing ``httpx.AsyncClient`` if provided (better for tests).
    cutoff_days:
        Skip any recalls older than *N* days.  Defaults to the value in
        ``settings.CPSC_CUTOFF_DAYS``.

    Returns
    -------
    int
        Number of recalls inserted.
    """

    settings = get_settings()
    cutoff_days = cutoff_days or settings.CPSC_CUTOFF_DAYS
    cutoff_date = datetime.now(tz=UTC) - timedelta(days=cutoff_days)

    owns_client = http_client is None
    if owns_client:
        timeout = httpx.Timeout(10.0, connect=5.0)
        http_client = httpx.AsyncClient(timeout=timeout)

    new_recalls: List[Dict[str, Any]] = []
    page = 1
    while True:
        params = {
            "PageNumber": page,
            "RecallStartDate": cutoff_date.strftime("%m-%d-%Y"),
            # page size is implicitly 20; we can change only via header, not query
        }

        try:
            resp = await http_client.get(CPSC_ENDPOINT, params=params)
            resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("CPSC request failed on page %s – %s", page, exc)
            break  # early exit, we'll retry next run

        data: Sequence[Dict[str, Any]] = resp.json()
        if not data:
            break  # no more pages

        logger.debug("Fetched %s recalls from CPSC page %s", len(data), page)

        # Collect recallIDs we already know to short‑circuit quickly
        recall_ids = [int(item["RecallID"]) for item in data]
        existing_ids: set[int] = {
            r[0]
            for r in (
                await db.execute(
                    select(Recall.external_id).where(
                        Recall.source == RecallSource.CPSC,
                        Recall.external_id.in_(recall_ids),
                    )
                )
            ).scalars().all()
        }

        for raw in data:
            rid = int(raw["RecallID"])
            if rid in existing_ids:
                # We assume results are ordered newest‑first, so hitting an
                # existing ID indicates we've already ingested older pages.
                logger.debug("Recall %s already exists – stopping pagination", rid)
                break

            recall_date = _parse_date(raw["RecallDate"])
            if recall_date < cutoff_date:
                logger.debug("Recall %s older than cutoff – stopping pagination", rid)
                break

            new_recalls.append(_normalise(raw))
        else:  # only executed if the for‑loop didn't break
            page += 1
            await asyncio.sleep(0.25)  # be polite to the API
            continue
        break  # break the while True if inner loop hit break

    if new_recalls:
        await _bulk_insert(db, new_recalls)
    logger.info("CPSC fetch complete – inserted %s new recalls", len(new_recalls))

    if owns_client:
        await http_client.aclose()

    return len(new_recalls)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_date(date_str: str) -> datetime:
    """Convert *MM/DD/YYYY* string into *UTC‑naive* ``datetime``"""
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").replace(tzinfo=UTC)
    except ValueError:
        logger.warning("Invalid date format from CPSC: %s", date_str)
        return datetime.now(tz=UTC)


def _normalise(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Map CPSC JSON structures onto our Recall ORM fields."""
    return {
        "source": RecallSource.CPSC,
        "external_id": int(raw["RecallID"]),
        "recall_date": _parse_date(raw["RecallDate"]),
        "title": raw.get("Title", "").strip(),
        "hazard": raw.get("Hazard", "").strip(),
        "description": raw.get("Description", "").strip(),
        "remedy": raw.get("Remedy", "").strip(),
        "url": raw.get("URL", "").strip() or raw.get("RecallURL", "").strip(),
        "image_url": (raw.get("Images", [{}])[0] or {}).get("URL", "").strip(),
        "created_at": datetime.now(tz=UTC),
    }


async def _bulk_insert(db: AsyncSession, rows: List[Dict[str, Any]]) -> None:
    """Perform a fast *ON CONFLICT DO NOTHING* bulk insert."""
    if not rows:
        return

    stmt = (
        insert(Recall)
        .values(rows)
        .on_conflict_do_nothing(index_elements=[Recall.source, Recall.external_id])
    )
    await db.execute(stmt)
    await db.commit()


# ---------------------------------------------------------------------------
# APScheduler wiring
# ---------------------------------------------------------------------------

def register_job(scheduler=None) -> None:
    """Register the CPSC fetch task with the (async) scheduler."""
    scheduler = scheduler or get_scheduler()
    settings = get_settings()
    scheduler.add_job(
        _scheduled_runner,
        "interval",
        minutes=settings.CPSC_POLL_MINUTES,
        id="fetch_cpsc",
        replace_existing=True,
    )
    logger.info("Scheduled CPSC fetch every %s min", settings.CPSC_POLL_MINUTES)


async def _scheduled_runner() -> None:
    """Get a fresh DB session and call :pyfunc:`fetch_cpsc`.  Wrapper required
    so APScheduler can run it without arguments.
    """
    from backend.db.session import async_session_factory  # local import to avoid cycles

    async with async_session_factory() as session:
        await fetch_cpsc(session)
