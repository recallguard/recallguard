from backend.utils.notifications import match_subscriptions, queue_notifications
from backend.db import init_db
from backend.utils.session import SessionLocal
from sqlalchemy import text
import responses


def test_match_subscriptions(tmp_path, monkeypatch):


    db = tmp_path / 'n.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db}')

    init_db()
    with SessionLocal() as db:
        db.execute(text("INSERT INTO subscriptions (user_id, recall_source, product_query) VALUES (1, 'cpsc', 'Widget')"))
        db.commit()
        recall = {'id': '1', 'product': 'Widget stroller', 'source': 'cpsc'}
        matches = match_subscriptions(db, recall)
    assert matches and matches[0]['user_id'] == 1
    SessionLocal.remove()


def test_queue_notifications_inserts(tmp_path, monkeypatch):


    db = tmp_path / 'n2.db'
    monkeypatch.setenv('DATABASE_URL', f'sqlite:///{db}')

    init_db()
    with SessionLocal() as db:
        db.execute(text("INSERT INTO subscriptions (user_id, recall_source, product_query) VALUES (1, 'cpsc', 'Widget')"))
        db.commit()
        recall = {'id': '2', 'product': 'Widget seat', 'source': 'cpsc'}
        monkeypatch.setenv('SENDGRID_API_KEY', '')
        monkeypatch.setenv('SLACK_WEBHOOK_URL', 'http://example.com/web')
        with responses.RequestsMock() as rsps:
            rsps.add(responses.POST, 'http://example.com/web', status=200)
            sent = queue_notifications(db, recall)
        assert sent == 1
        count = db.execute(text('SELECT COUNT(*) FROM sent_notifications')).fetchone()[0]
        assert count == 1
    SessionLocal.remove()
