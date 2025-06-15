"""Fetch recalls from the NHTSA API."""
from typing import List, Dict


def fetch() -> List[Dict]:
    """Return vehicle-related recalls.
    This placeholder would normally call the NHTSA API.
    """
    return [{"source": "NHTSA", "title": "Vehicle recall", "product": "Car"}]

