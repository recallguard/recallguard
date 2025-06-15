"""Fetch recalls from the CPSC API."""
from typing import List, Dict


def fetch() -> List[Dict]:
    """Return a list of recalls from the CPSC.

    This is a placeholder implementation that would normally call the
    official CPSC API.
    """
    return [{"source": "CPSC", "title": "Sample recall", "product": "Widget"}]

