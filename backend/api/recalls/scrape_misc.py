"""Scrape miscellaneous recall sources."""
from typing import List, Dict


def fetch(use_cache: bool = True) -> List[Dict]:
    """Return recalls scraped from websites that do not have APIs."""
    return [{"source": "Misc", "title": "Other recall", "product": "Toy"}]

