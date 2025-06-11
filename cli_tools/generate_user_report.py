"""
cli_tools/generate_user_report.py
=================================
Generate a quick metric report for all RecallGuard users.

The script connects to the primary DB, aggregates per-user data
(products owned, pending alerts, subscription tier, etc.) and then
outputs either:

* A **pretty table** to stdout  (default format)
* A **CSV file** (if --format csv and --out PATH are supplied)

Usage
-----

# Pretty table for *all* users
python -m cli_tools.generate_user_report

# CSV for users created since 2025-01-01
python -m cli_tools.generate_user_report --format csv --out ./report.csv --since 2025-01-01
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import sys
from pathlib import Path
from typing import Iterable, List

from sqlalchemy import func, select
from tabulate import tabulate

from backend.db.models import Alert, Product, SessionLocal, User
from backend.utils.config import get_settings
from backend.utils.logging import setup_logging

settings = get_settings()
setup_logging()

# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate RecallGuard user metrics report")
    parser.add_argument(
        "--format",
        choices=("table", "csv"),
        default="table",
        help="Output format (default: table)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="If --format=csv, path to write the CSV (defaults to stdout)",
    )
    parser.add_argument(
        "--since",
        type=lambda s: dt.datetime.strptime(s, "%Y-%m-%d").date(),
        default=None,
        help="Only include users created on/after this YYYY-MM-DD date",
    )
    return parser.parse_args(argv)


def fetch_user_metrics(created_since: dt.date | None = None) -> List[dict]:
    """Return a list of dicts, one per user, with aggregated metrics."""
    with SessionLocal() as db:
        q = (
            db.query(
                User.id.label("user_id"),
                User.email,
                User.created_at,
                User.tier.label("plan"),
                func.count(Product.id).label("products"),
                func.count(Alert.id).filter(Alert.sent_at.is_(None)).label("pending_alerts"),
            )
            .outerjoin(Product, Product.user_id == User.id)
            .outerjoin(Alert, Alert.user_id == User.id)
            .group_by(User.id)
            .order_by(User.created_at)
        )

        if created_since:
            q = q.filter(User.created_at >= created_since)

        rows = q.all()

    return [dict(r._mapping) for r in rows]  # SQLAlchemy Row → dict


def render_table(rows: list[dict]) -> str:
    headers = {
        "user_id": "ID",
        "email": "Email",
        "created_at": "Joined",
        "plan": "Plan",
        "products": "# Products",
        "pending_alerts": "Pending Alerts",
    }
    table = tabulate(
        [[row[key] for key in headers] for row in rows],
        headers=list(headers.values()),
        tablefmt="github",
        numalign="right",
    )
    return table


def write_csv(rows: list[dict], path: Path | None):
    headers = ["user_id", "email", "created_at", "plan", "products", "pending_alerts"]
    writer: csv.writer
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        fp = path.open("w", newline="", encoding="utf-8")
        close_fp = True
    else:
        fp = sys.stdout
        close_fp = False

    try:
        writer = csv.writer(fp)
        writer.writerow(headers)
        for r in rows:
            writer.writerow([r[h] for h in headers])
    finally:
        if close_fp:
            fp.close()


# ──────────────────────────────────────────────────────────────────────────────
# Entry-point
# ──────────────────────────────────────────────────────────────────────────────


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)

    rows = fetch_user_metrics(created_since=args.since)
    if not rows:
        print("No users found for given criteria.", file=sys.stderr)
        sys.exit(0)

    if args.format == "table":
        print(render_table(rows))
    else:  # csv
        write_csv(rows, args.out)
        dest = args.out if args.out else "stdout"
        print(f"CSV written to {dest}", file=sys.stderr)


if __name__ == "__main__":  # pragma: no cover
    main()
