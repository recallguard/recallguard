from flask import Blueprint, jsonify, Response, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from time import time
from datetime import datetime
from sqlalchemy import text
from backend.utils.session import get_engine

bp = Blueprint('ops', __name__)

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'http_status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Request latency', ['endpoint'])
SCHEDULER_JOBS = Counter('scheduler_jobs_total', 'Scheduled jobs executed')


@bp.route('/healthz')
def healthz():
    start = time()
    engine = get_engine()
    try:
        if getattr(engine, '_disposed', False):
            raise RuntimeError('engine disposed')
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        status = 200
        payload = {'status': 'ok', 'db': 'ok'}
    except Exception:
        status = 503
        payload = {'status': 'error', 'db': 'down'}
    REQUEST_COUNT.labels(method=request.method, endpoint='/healthz', http_status=status).inc()
    REQUEST_LATENCY.labels(endpoint='/healthz').observe(time() - start)
    return jsonify(payload), status


@bp.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@bp.route('/latency')
def avg_latency():
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT recall_date, fetched_at FROM recalls WHERE recall_date IS NOT NULL AND fetched_at IS NOT NULL")
        ).fetchall()
    vals = []
    for r in rows:
        try:
            recall_dt = datetime.fromisoformat(r._mapping["recall_date"])
            fetched_dt = datetime.fromisoformat(r._mapping["fetched_at"])
            vals.append((fetched_dt - recall_dt).total_seconds())
        except Exception:
            pass
    avg = sum(vals) / len(vals) if vals else 0
    return jsonify({"average_latency_seconds": avg})
