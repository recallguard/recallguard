"""backend/api/recalls/fetch_usda.py
==================================
Fetch **USDA FSIS (Food Safety and Inspection Service)** meat & poultry
recall notices and persist only *new* records into the ``recalls`` table.

Data source
-----------
The FSIS publishes an **Atom** feed for active recalls plus a complete CSV
archive.  The Atom feed gives us the *latest* activity without having to
re‑download the full dataset every run.  We use the feed as our primary
source and fall back to the CSV for back‑filling older recalls when the DB
is empty.

Feed:   https://www.fsis.usda.gov/feeds/recalls.xml
Archive: https://www.fsis.usda.gov/sites/default/files/recalls/recall-case-archive.csv

We poll the feed every ``USDA_POLL_MINUTES`` (default 60).  Each entry is
uniquely identified by the *recall number* (e.g. "017‑2024").  We stop as
soon as we hit a recall already present in the DB **or** when the publish
 date is older than ``cutoff_days``.
"""
from __future__ import annotations

import asyncio
import csv
import datetime as dt
import io
import logging
from typing import Any, Dict, List, Tuple

import httpx
from bs4 import BeautifulSoup  # html/xml parsing for Atom
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Recall, RecallSource
from backend.utils.config import get_settings
from backend.utils.logging import get_logger
from backend.utils.scheduler import get_scheduler

logger = get_logger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
ATOM_FEED_URL = "https://www.fsis.usda.gov/feeds/recalls.xml"
ARCHIVE_CSV_URL = (
    "https://www.fsis.usda.gov/sites/default/files/recalls/recall-case-archive.csv"
)
CUT_OFF_DAYS = settings.RECALL_CUTOFF_DAYS  # fallback 365
PAGE_FETCH_TIMEOUT = 15.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_atom_entry(entry: "bs4.element.Tag") -> Dict[str, Any]:
    """Extract relevant fields from an Atom feed <entry>."""
    recall_number = entry.find("title").text.split(" ")[0].strip()
    published_str = entry.find("published").text.strip()
    pub_date = dt.datetime.fromisoformat(published_str.replace("Z", "+00:00"))

    summary_html = entry.find("summary").text.strip()
    # strip HTML tags
    summary_text = BeautifulSoup(summary_html, "lxml").get_text(" ", strip=True)

    link = entry.find("link").get("href")

    return {
        "recall_number": recall_number,
        "pub_date": pub_date,
        "summary": summary_text,
        "url": link,
    }


def _normalise(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Map parsed entry to Recall ORM column dictionary."""
    return {
        "external_id": entry["recall_number"],
        "source": RecallSource.USDA,
        "title": f"USDA Recall {entry['recall_number']}",
        "summary": entry["summary"],
        "url": entry["url"],
        "date": entry["pub_date"],
    }


async def _existing_ids(session: AsyncSession) -> set[str]:
    q = select(Recall.external_id).where(Recall.source == RecallSource.USDA)
    rows = (await session.execute(q)).scalars().all()
    return set(rows)


async def _bulk_insert(session: AsyncSession, records: List[Dict[str, Any]]) -> int:
    if not records:
        return 0
    stmt = insert(Recall).values(records).on_conflict_do_nothing(
        index_elements=[Recall.external_id]
    )
    result = await session.execute(stmt)
    await session.commit()
    return result.rowcount or 0


# ---------------------------------------------------------------------------
# Main fetch coroutine
# ---------------------------------------------------------------------------


async def fetch_usda(session_factory) -> int:
    """Fetch the USDA Atom feed and persist new recalls.

    Returns the number of new rows inserted.
    """
    async with session_factory() as session:  # type: AsyncSession
        existing = await _existing_ids(session)
        cutoff = dt.datetime.utcnow() - dt.timedelta(days=CUT_OFF_DAYS)

    async with httpx.AsyncClient(timeout=PAGE_FETCH_TIMEOUT) as client:
        resp = await client.get(ATOM_FEED_URL)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "xml")
        entries = soup.find_all("entry")

    new_records: List[Dict[str, Any]] = []
    for entry in entries:
        parsed = _parse_atom_entry(entry)
        if parsed["recall_number"] in existing:
            # we reached a recall already ingested—stop processing
            break
        if parsed["pub_date"] < cutoff:
            break
        new_records.append(_normalise(parsed))

    async with session_factory() as session:
        inserted = await _bulk_insert(session, new_records)

    logger.info("USDA fetch complete – %s new recalls", inserted)
    return inserted


# ---------------------------------------------------------------------------
# One‑off back‑fill helper (CSV)
# ---------------------------------------------------------------------------


async def backfill_from_csv(session_factory) -> int:
    """Import older recalls using the CSV archive (idempotent)."""
    async with httpx.AsyncClient(timeout=PAGE_FETCH_TIMEOUT) as client:
        resp = await client.get(ARCHIVE_CSV_URL)
        resp.raise_for_status()
        csv_file = io.StringIO(resp.text)
        reader = csv.DictReader(csv_file)
        rows = list(reader)

    async with session_factory() as session:
        existing = await _existing_ids(session)
        new_records: List[Dict[str, Any]] = []
        for row in rows:
            recall_number = row["Recall Number"].strip()
            if recall_number in existing:
                continue
            pub_date = dt.datetime.strptime(row["Release Date"], "%m/%d/%Y")
            if pub_date < dt.datetime.utcnow() - dt.timedelta(days=CUT_OFF_DAYS):
                continue
            new_records.append(
                _normalise(
                    {
                        "recall_number": recall_number,
                        "pub_date": pub_date,
                        "summary": row["Summary"],
                        "url": row["URL"],
                    }
                )
            )
        inserted = await _bulk_insert(session, new_records)

    logger.info("USDA CSV back‑fill inserted %s rows", inserted)
    return inserted


# ---------------------------------------------------------------------------
# Scheduler hook
# ---------------------------------------------------------------------------


def register_job(scheduler=None, session_factory=None) -> None:
    """Register the periodic fetch job with the project‑wide scheduler."""
    scheduler = scheduler or get_scheduler()
    session_factory = session_factory or settings.get_session_factory()
    scheduler.add_job(
        fetch_usda,
        "interval",
        minutes=settings.USDA_POLL_MINUTES,
        id="fetch_usda_recalls",
        kwargs={"session_factory": session_factory},
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=300,
    )
    logger.info("Scheduled USDA recall fetch every %s minutes", settings.USDA_POLL_MINUTES)


# If the scheduler starts automatically on import (e.g. Celery beat fashion)
# uncomment the following:
# register_job()
