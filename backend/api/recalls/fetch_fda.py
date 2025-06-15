"""Fetch recalls from the FDA API."""
from typing import List, Dict


def fetch() -> List[Dict]:
    """Return a list of FDA recalls.

    Placeholder implementation that would fetch data from the FDA API.
    """
    return [{"source": "FDA", "title": "FDA recall", "product": "Medication"}]

