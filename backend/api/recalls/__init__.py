"""Recall fetcher utilities."""

from .fetch_cpsc import fetch as fetch_cpsc
from .fetch_fda import fetch as fetch_fda
from .fetch_usda import fetch as fetch_usda
from .fetch_nhtsa import fetch as fetch_nhtsa
from .scrape_misc import fetch as fetch_misc


def fetch_all(use_cache: bool = True) -> list:
    """Return recalls from all available sources."""
    recalls = []
    for func in (fetch_cpsc, fetch_fda, fetch_usda, fetch_nhtsa, fetch_misc):
        recalls.extend(func(use_cache=use_cache))
    return recalls
from .router import router
