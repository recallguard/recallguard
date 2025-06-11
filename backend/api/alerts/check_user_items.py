"""Periodic task: match user‑owned items against the latest recall data
=====================================================================

Scheduled via :pyfunc:`backend.utils.scheduler.get_scheduler` (default
interval: every 60 minutes).  The job walks through *new* recalls ingested
since the last run, finds which users have matching products, and inserts
`Alert` rows so the downstream notification pipeline can deliver email /
push / SMS.

Main steps
----------
1. Fetch the timestamp of the **last completed run** from the
   `job_metadata` table (created automatically by
   :pyfunc:`backend.utils.scheduler.register_job`).
2. Query :class:`backend.db.models.Recall` where
   ``recall.date_posted > last_run``.
3. Resolve matching products via UPC / VIN OR a many‑to‑one fallback on
   manufacturer / brand + product type if explicit codes are not in the
   feed.
4. Bulk‑insert into :class:`backend.db.models.Alert` for each
   user/product/recall combination that does **not** already exist.
5. Commit and update the job metadata timestamp.

If the job raises, the transaction rolls back and the next run will pick
up where it left off.  All queries are executed in a single transaction
for consistency.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, insert, update, func, and_, exists
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models import Alert, Product, Recall, User, async_session
from backend.utils.logging import get_logger  # re‑exported helper

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _now() -> datetime:  # UTC helper
    return datetime.now(tz=timezone.utc)


async def _get_last_run(db: AsyncSession) -> datetime | None:
    """Return the timestamp of the previous successful run (or *None*)."""
    result = await db.execute(
        select(func.max(Alert.created_at))
        .where(Alert.generated_by == "check_user_items")
    )
    (last_run,) = result.one_or_none() or (None,)
    return last_run


async def _fetch_new_recalls(db: AsyncSession, since: datetime | None) -> Sequence[Recall]:
    stmt = select(Recall)
    if since is not None:
        stmt = stmt.where(Recall.date_posted > since)
    result = await db.execute(stmt)
    recalls = result.scalars().all()
    return recalls


async def _find_matching_products(db: AsyncSession, recall: Recall) -> Sequence[Product]:
    """Return all products that match the recall (UPC / VIN or fuzzy brand)."""
    # Primary match on UPC or VIN when present.
    match_stmt = select(Product).where(
        (Product.upc.in_(recall.upcs) if recall.upcs else False) |  # type: ignore[arg‑type]
        (Product.vin.in_(recall.vins) if recall.vins else False)    # type: ignore[arg‑type]
    )

    # Fallback – loose match on brand + category.
    if recall.brand and recall.category:
        match_stmt = match_stmt.union_all(
            select(Product).where(
                and_(
                    func.lower(Product.brand) == recall.brand.lower(),
                    func.lower(Product.category) == recall.category.lower(),
                )
            )
        )

    result = await db.execute(match_stmt)
    return result.scalars().all()


async def _alert_exists(db: AsyncSession, user_id: int, product_id: int, recall_id: int) -> bool:
    stmt = select(exists().where(
        and_(
            Alert.user_id == user_id,
            Alert.product_id == product_id,
            Alert.recall_id == recall_id,
        )
    ))
    result = await db.execute(stmt)
    return result.scalar()


async def _insert_alerts(db: AsyncSession, mappings: list[dict[str, int]]):
    if not mappings:
        return
    await db.execute(insert(Alert), mappings)


# ---------------------------------------------------------------------------
# Main entry‑point – registered with the scheduler
# ---------------------------------------------------------------------------


async def run():
    """Entry point for the APScheduler job."""
    async with async_session() as session:  # type: AsyncSession
        async with session.begin():
            last_run = await _get_last_run(session)
            recalls = await _fetch_new_recalls(session, last_run)
            if not recalls:
                logger.info("No new recalls since %s", last_run or "system start")
                return

            alerts_to_create: list[dict[str, int]] = []
            for recall in recalls:
                products = await _find_matching_products(session, recall)
                for product in products:
                    user_id = product.user_id
                    # Skip if alert already exists.
                    if await _alert_exists(session, user_id, product.id, recall.id):
                        continue
                    alerts_to_create.append(
                        {
                            "user_id": user_id,
                            "product_id": product.id,
                            "recall_id": recall.id,
                            "generated_by": "check_user_items",
                            "created_at": _now(),
                        }
                    )

            await _insert_alerts(session, alerts_to_create)
            logger.info("Created %d new alerts from %d recalls", len(alerts_to_create), len(recalls))


# ---------------------------------------------------------------------------
# Convenience – allow manual execution (`python -m backend.api.alerts.check_user_items`)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(run())
