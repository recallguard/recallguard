"""Data refresh utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

<<<<<<< HEAD
=======
from datetime import datetime

>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
from backend.api.recalls import fetch_cpsc, fetch_fda, fetch_nhtsa, fetch_usda
from backend.utils import db as db_utils
from backend.utils.config import get_db_path


def refresh_recalls(db_path: Path | None = None) -> Dict[str, int]:
    """Fetch latest recalls and upsert into the database."""
    if db_path is None:
        db_path = Path(get_db_path())

    conn = db_utils.connect(db_path)
    new = 0
    updated = 0

    recalls: List[Dict] = []
    for func in (fetch_cpsc, fetch_fda, fetch_nhtsa, fetch_usda):
        recalls.extend(func(use_cache=False))

    for r in recalls:
        existing = conn.execute(
            "SELECT id FROM recalls WHERE id=? AND source=?", (r.get("id"), r.get("source"))
        ).fetchone()
        if existing:
            conn.execute(
<<<<<<< HEAD
                "UPDATE recalls SET product=?, hazard=?, recall_date=? WHERE id=? AND source=?",
                (r.get("product"), r.get("hazard"), r.get("recall_date"), r.get("id"), r.get("source")),
=======
                "UPDATE recalls SET product=?, hazard=?, recall_date=?, fetched_at=? "
                "WHERE id=? AND source=?",
                (
                    r.get("product"),
                    r.get("hazard"),
                    r.get("recall_date"),
                    datetime.utcnow().isoformat(),
                    r.get("id"),
                    r.get("source"),
                ),
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
            )
            updated += 1
        else:
            conn.execute(
<<<<<<< HEAD
                "INSERT INTO recalls (id, product, hazard, recall_date, source) VALUES (?, ?, ?, ?, ?)",
                (r.get("id"), r.get("product"), r.get("hazard"), r.get("recall_date"), r.get("source")),
=======
                "INSERT INTO recalls (id, product, hazard, recall_date, source, fetched_at) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    r.get("id"),
                    r.get("product"),
                    r.get("hazard"),
                    r.get("recall_date"),
                    r.get("source"),
                    datetime.utcnow().isoformat(),
                ),
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
            )
            new += 1
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM recalls").fetchone()[0]
    conn.close()

    summary = {"new": new, "updated": updated, "total": total}
    print(summary)
    return summary
