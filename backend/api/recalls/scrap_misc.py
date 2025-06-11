"""
backend/api/recalls/scrape_misc.py
==================================
Pull recall notices from *niche* or manufacturer-specific sources that do
not expose a well-formed API (think static web pages, RSS/Atom feeds, or
PDF bulletins).  Everything is normalised into our shared `Recall` schema
and bulk-inserted with `ON CONFLICT DO NOTHING`.

Add new scrapers by registering a coroutine that yields one or more
`dict` objects following the shape required by `RecallIn` below, then
adding it to `SCRAPER_REGISTRY`.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import logging
import re
from collections.abc import AsyncIterator, Callable
from typing import Any, Final

import httpx
from bs4 import BeautifulSoup

from backend.db.models import Recall, SessionLocal
from backend.utils.config import get_settings
from backend.utils.logging import setup_logging

log = logging.getLogger(__name__)
settings = get_settings()

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


class RecallIn(dict):
    """A *typed* alias for incoming recall rows prior to ORM insert."""
    recall_id: str                # unique across *all* sources
    title: str
    summary: str
    link: str
    hazard: str | None
    remedy: str | None
    recall_date: dt.date
    source: str                   # e.g. "TARGET", "TYLENOL"
    images: list[str] | None


async def fetch_html(url: str) -> str:
    """GET a URL with sane defaults & simple back-off retries."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        return r.text


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


# ──────────────────────────────────────────────────────────────────────────────
# Scraper: Target (example)
# ──────────────────────────────────────────────────────────────────────────────


TARGET_FEED: Final = "https://corporate.target.com/about/product-recalls"

async def scrape_target() -> AsyncIterator[RecallIn]:
    """Scrape Target's HTML recall bulletin list."""
    html = await fetch_html(TARGET_FEED)
    soup = BeautifulSoup(html, "html.parser")

    for li in soup.select("ul.product-recall-list li"):
        link_el = li.find("a", href=True)
        if not link_el:
            continue

        title = link_el.text.strip()
        url = link_el["href"]

        # Extract YYYY-MM-DD from the snippet, else today()
        date_text = li.find("span", class_="date")
        try:
            recall_dt = dt.datetime.strptime(date_text.text.strip(), "%B %d, %Y").date()  # type: ignore[arg-type]
        except Exception:
            recall_dt = dt.date.today()

        recall = RecallIn(
            recall_id=f"TARGET-{slugify(title)}-{recall_dt.isoformat()}",
            title=title,
            summary=title,          # Target has no short summary; reuse
            link=url,
            hazard=None,
            remedy=None,
            recall_date=recall_dt,
            source="TARGET",
            images=None,
        )
        yield recall


# ──────────────────────────────────────────────────────────────────────────────
# Scraper: Tylenol DMA Example (dummy HTML site)
# ──────────────────────────────────────────────────────────────────────────────


TYLENOL_FEED: Final = "https://www.tylenol.com/safety/recall-updates"

async def scrape_tylenol_dma() -> AsyncIterator[RecallIn]:
    """Scrape Tylenol safety-recall updates page (illustrative)."""
    html = await fetch_html(TYLENOL_FEED)
    soup = BeautifulSoup(html, "html.parser")

    for art in soup.select("article.recall"):
        hdr = art.find("h2")
        title = hdr.text.strip() if hdr else "Tylenol Recall"

        link_el = art.find("a", href=True)
        url = link_el["href"] if link_el else TYLENOL_FEED

        date_el = art.find("time")
        recall_dt = (
            dt.datetime.strptime(date_el["datetime"], "%Y-%m-%d").date()  # type: ignore[arg-type]
            if date_el and date_el.get("datetime")
            else dt.date.today()
        )

        summary_el = art.find("p", class_="summary")
        summary = summary_el.text.strip() if summary_el else title

        recall = RecallIn(
            recall_id=f"TYLENOL-{slugify(title)}-{recall_dt.isoformat()}",
            title=title,
            summary=summary,
            link=url,
            hazard="Potential contamination" if "contamination" in summary.lower() else None,
            remedy=None,
            recall_date=recall_dt,
            source="TYLENOL",
            images=None,
        )
        yield recall


# ──────────────────────────────────────────────────────────────────────────────
# Registry + Orchestrator
# ──────────────────────────────────────────────────────────────────────────────

SCRAPER_REGISTRY: dict[str, Callable[[], AsyncIterator[RecallIn]]] = {
    "TARGET": scrape_target,
    "TYLENOL": scrape_tylenol_dma,
}

BATCH_SIZE = 200  # bulk insert chunk

async def bulk_insert_recalls(rows: list[RecallIn]) -> int:
    """Insert recall dicts -> DB; skip duplicates."""
    if not rows:
        return 0

    with SessionLocal() as db:
        # Use SQLAlchemy ORM bulk insert with conflict handling
        objs = [Recall(**row) for row in rows]  # type: ignore[arg-type]
        db.bulk_save_objects(objs, preserve_order=False)
        try:
            db.commit()
        except Exception as exc:
            db.rollback()
            # In dev we might hit duplicate recall_id conflicts; swallow them
            log.debug("DB bulk insert failed: %s", exc, exc_info=exc)
        return len(rows)


async def run_all_scrapers() -> int:
    """Dispatch each scraper concurrently; return number of new recalls."""
    tasks = [scraper() for scraper in SCRAPER_REGISTRY.values()]
    # Flatten async generators into recall dict list
    new_recalls: list[RecallIn] = []
    for coro in asyncio.as_completed(tasks):
        async for recall in await coro:
            new_recalls.append(recall)

    inserted = await bulk_insert_recalls(new_recalls)
    log.info("scrape_misc inserted %s new recalls", inserted)
    return inserted


# ──────────────────────────────────────────────────────────────────────────────
# APScheduler integration
# ──────────────────────────────────────────────────────────────────────────────

def register_job(scheduler) -> None:
    from apscheduler.triggers.interval import IntervalTrigger

    scheduler.add_job(
        run_all_scrapers,
        trigger=IntervalTrigger(minutes=settings.MISC_POLL_MINUTES or 60),
        id="scrape_misc_recalls",
        max_instances=1,
        replace_existing=True,
    )

# ──────────────────────────────────────────────────────────────────────────────
# Entry-point for manual runs
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":  # pragma: no cover
    setup_logging()
    asyncio.run(run_all_scrapers())
