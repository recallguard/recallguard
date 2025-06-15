from pathlib import Path
from backend.api.alerts.check_user_items import check_user_items
from backend.db import create_tables
from backend.db.models import Recall
from backend.utils.db import get_session, ENGINE


def test_check_user_items():
    db = Path("dev.db")
    ENGINE.dispose()
    if db.exists():
        db.unlink()
    create_tables()
    with get_session() as session:
        session.add(Recall(source="TEST", product="Widget"))
    items = ["widget", "Gadget"]
    assert check_user_items(items) == ["widget"]

