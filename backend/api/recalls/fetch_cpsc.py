"""Fetch recalls from the CPSC API.

This sample implementation reads from a local JSON file to avoid network
dependencies. In a production system this module would perform authenticated
requests to the official CPSC API and return the latest recalls.
"""

from pathlib import Path
from typing import List, Dict
import json


DATA_FILE = Path(__file__).resolve().parents[3] / "data" / "cpsc_sample.json"


def fetch() -> List[Dict]:
    """Return a list of recalls from the CPSC sample data."""
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as fh:
        records = json.load(fh)
    # Normalize keys to maintain a consistent shape across sources
    return [
        {
            "source": "CPSC",
            "id": r.get("RecallID"),
            "title": r.get("Title"),
            "product": r.get("Product"),
            "url": r.get("URL"),
        }
        for r in records
    ]

