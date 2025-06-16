"""Authentication helpers for password hashing and JWT handling."""
from datetime import datetime, timedelta
from os import getenv

from jose import JWTError, jwt
from passlib.hash import bcrypt
from functools import wraps
from flask import request, jsonify


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
