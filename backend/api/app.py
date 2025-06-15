from flask import Flask, jsonify, request

from .recalls import fetch_all
from .alerts import check_user_items, generate_summary

# simple in-memory store for user items
USER_ITEMS = []


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get('/recalls')
    def recalls_route():
        return jsonify(fetch_all())

    @app.post('/user-items')
    def add_item():
        data = request.get_json(force=True)
        item = data.get('item')
        if item:
            USER_ITEMS.append(item)
        return jsonify({'items': USER_ITEMS})

    @app.get('/alerts')
    def alerts_route():
        recalls = fetch_all()
        matches = check_user_items.check_user_items(USER_ITEMS, recalls)
        summaries = [generate_summary.generate_summary({'title': 'Recall', 'product': m}) for m in matches]
        return jsonify({'alerts': summaries})

    return app
