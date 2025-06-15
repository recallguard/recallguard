"""Match user items against known recalls."""
from __future__ import annotations

from typing import List
from sqlalchemy import select, func

from backend.db.models import Recall
from backend.utils.db import get_session


def check_user_items(user_items: List[str]) -> List[str]:
    """Return user items that appear in the recall list.

    Matching is case-insensitive using the database.
    """
    matches: List[str] = []
    if not user_items:
        return matches
    lowered = [item.lower() for item in user_items]
    with get_session() as session:
        stmt = select(Recall.product).where(func.lower(Recall.product).in_(lowered))
        recalled = {row[0].lower() for row in session.execute(stmt)}
    for item in user_items:
        if item.lower() in recalled:
            matches.append(item)
    return matches

