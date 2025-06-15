
from backend.db.models import Recall


def _serialize(recall: Recall) -> dict:
    """Convert a Recall ORM object to a serializable dict."""
    return {
        "id": recall.id,
        "source": recall.source,
        "product": recall.product,
        "hazard": recall.hazard,
        "recall_date": recall.recall_date.isoformat() if recall.recall_date else None,
        "url": recall.details_url,
    }

    recalls: list[dict] = []
        for recall in func():
            recalls.append(_serialize(recall))
from .fetch_cpsc import fetch as fetch_cpsc
from .fetch_fda import fetch as fetch_fda
from .fetch_usda import fetch as fetch_usda
from .fetch_nhtsa import fetch as fetch_nhtsa
from .scrape_misc import fetch as fetch_misc


def fetch_all() -> list:
    """Return recalls from all available sources."""
    recalls = []
    for func in (fetch_cpsc, fetch_fda, fetch_usda, fetch_nhtsa, fetch_misc):
        recalls.extend(func())
    return recalls


