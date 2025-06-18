from __future__ import annotations

from typing import Protocol


class RecallProto(Protocol):
    classification: str | None
    hazard: str | None


def classify_recall(recall: RecallProto) -> str:
    """Return 'urgent' if recall is high priority else 'digest'."""
    classification = (recall.classification or "").lower()
    hazard = (recall.hazard or "").lower()
    if classification == "class i":
        return "urgent"
    keywords = ["fire", "burn", "choking", "death"]
    if any(word in hazard for word in keywords):
        return "urgent"
    return "digest"
