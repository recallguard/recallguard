from pathlib import Path
from backend.db import create_tables
from backend.db.models import Recall, User
from backend.utils.db import get_session, ENGINE


def test_models_round_trip(tmp_path):
    db = Path("dev.db")
    ENGINE.dispose()
    if db.exists():
        db.unlink()
    create_tables()
    with get_session() as session:
        r = Recall(source="TEST", product="Gizmo")
        session.add(r)
    with get_session() as session:
        fetched = session.get(Recall, r.id)
        assert fetched and fetched.product == "Gizmo"

    with get_session() as session:
        u = User(email="example@example.com")
        session.add(u)
    with get_session() as session:
        fetched_u = session.get(User, u.id)
        assert fetched_u.email == "example@example.com"
