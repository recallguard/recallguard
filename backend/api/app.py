from flask import Flask, jsonify, request
from sqlalchemy import select, func

from .recalls import fetch_all, _serialize
from .alerts import check_user_items, generate_summary
from backend.db.models import Recall, UserItem
from backend.utils.db import get_session
from backend.db import create_tables

# simple in-memory store for user items
USER_ITEMS = []


def create_app() -> Flask:
    create_tables()
    app = Flask(__name__)

    @app.get('/recalls')
    def recalls_route():
        return jsonify(fetch_all())

    @app.get('/api/recalls')
    def api_recalls_route():
        limit = request.args.get('limit', '200')
        try:
            limit_val = min(int(limit), 500)
        except ValueError:
            limit_val = 200
        source = request.args.get('source')
        with get_session() as session:
            stmt = select(Recall)
            if source:
                stmt = stmt.where(func.lower(Recall.source) == source.lower())
            stmt = stmt.order_by(Recall.recall_date.desc()).limit(limit_val)
            recalls = session.scalars(stmt).all()
        return jsonify([_serialize(r) for r in recalls])

    @app.post('/user-items')
    def add_item():
        data = request.get_json(force=True)
        item = data.get('item')
        if item:
            USER_ITEMS.append(item)
        return jsonify({'items': USER_ITEMS})

    @app.get('/alerts')
    def alerts_route():
        fetch_all()
        matches = check_user_items.check_user_items(USER_ITEMS)
        summaries = [generate_summary.generate_summary({'title': 'Recall', 'product': m}) for m in matches]
        return jsonify({'alerts': summaries})

    @app.get('/api/alerts')
    def api_alerts_route():
        user_id = int(request.args.get('user', '1'))
        with get_session() as session:
            items = [row[0] for row in session.execute(select(UserItem.item_name).where(UserItem.user_id == user_id))]
        matches = check_user_items.check_user_items(items)
        if not matches:
            return jsonify([])
        lowered = [m.lower() for m in matches]
        with get_session() as session:
            stmt = select(Recall).where(func.lower(Recall.product).in_(lowered))
            stmt = stmt.order_by(Recall.recall_date.desc())
            recalls = session.scalars(stmt).all()
        return jsonify([_serialize(r) for r in recalls])

    return app
