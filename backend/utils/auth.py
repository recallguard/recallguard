"""Authentication helpers for password hashing and JWT handling."""
from datetime import datetime, timedelta
from os import getenv

from jose import JWTError, jwt
from passlib.hash import bcrypt
from functools import wraps
from flask import request, jsonify
from sqlalchemy import text
from backend.utils.db import connect
from backend.db.models import stripe_customers


def hash_password(pwd: str) -> str:
    """Return a bcrypt hash for the given password."""
    return bcrypt.hash(pwd)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a hash."""
    try:
        return bcrypt.verify(plain, hashed)
    except ValueError:
        return False


def create_access_token(data: dict, expires_minutes: int = 1440) -> str:
    """Create a signed JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode["exp"] = expire
    secret = getenv("JWT_SECRET", "change-me")
    return jwt.encode(to_encode, secret, algorithm="HS256")


def decode_access_token(token: str):
    """Decode a JWT and return the payload or None."""
    secret = getenv("JWT_SECRET", "change-me")
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
    except JWTError:
        return None



def jwt_required(fn):
    """Decorator to protect routes with JWT auth."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "unauthorized"}), 401
        token = auth.split(" ", 1)[1]
        payload = decode_access_token(token)
        if not payload:
            return jsonify({"error": "unauthorized"}), 401
        request.user = payload
        return fn(*args, **kwargs)

    return wrapper


def get_jwt_subject() -> dict:
    """Return the decoded JWT payload set by ``jwt_required``."""
    return getattr(request, 'user', {})


def require_plan(required: str):
    """Decorator to enforce a minimum subscription plan on a route."""
    tiers = {"free": 0, "pro": 1, "enterprise": 2}

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = get_jwt_subject()
            uid = user.get("user_id")
            if not uid:
                return jsonify({"error": "unauthorized"}), 401
            with connect() as conn:
                row = conn.execute(
                    text("SELECT plan FROM stripe_customers WHERE user_id=:u"),
                    {"u": uid},
                ).fetchone()
            plan = row._mapping["plan"] if row else "free"
            if tiers.get(plan, 0) < tiers.get(required, 0):
                return jsonify({"error": "upgrade required"}), 402
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def track_quota(fn):
    """Decrement monthly quota and block when exhausted."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = get_jwt_subject()
        uid = user.get("user_id")
        if not uid:
            return jsonify({"error": "unauthorized"}), 401
        with connect() as conn:
            row = conn.execute(
                stripe_customers.select().where(stripe_customers.c.user_id == uid)
            ).fetchone()
            if not row:
                conn.execute(
                    stripe_customers.insert().values(
                        user_id=uid, plan="free", quota=100, seats=1
                    )
                )
                conn.commit()
                quota = 100
                plan = "free"
            else:
                quota = row._mapping["quota"]
                plan = row._mapping["plan"]
            if plan != "enterprise":
                if quota <= 0:
                    return jsonify({"error": "quota exceeded"}), 429
                conn.execute(
                    stripe_customers.update()
                    .where(stripe_customers.c.user_id == uid)
                    .values(quota=quota - 1)
                )
                conn.commit()
        return fn(*args, **kwargs)

    return wrapper
