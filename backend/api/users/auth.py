"""backend/api/users/auth.py
====================================
JWT-based authentication & authorisation routes for RecallGuard.

Implements a straightforward **OAuth2 Password-Bearer** flow with JSON Web
Tokens (JWT) for stateless session management.

Routes
------
* **POST /auth/register** – Create a new local user account.
* **POST /auth/login**    – Exchange credentials for a short-lived access
  token (JWT).
* **GET  /auth/me**       – Retrieve the currently-authenticated user (must
  include ``Authorization: Bearer <token>``).

The implementation purposefully avoids refresh tokens for now – clients can
simply re-authenticate when the 1-hour access token expires.  You can tweak
``ACCESS_TOKEN_EXPIRE_MINUTES`` in ``settings`` if needed.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Generator, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from backend.db.models import SessionLocal, User
from backend.utils.config import get_settings

# ─────────────────────────────────────────────────────────────────────────────
# Module-level constants & helpers
# ─────────────────────────────────────────────────────────────────────────────

log = logging.getLogger(__name__)
settings = get_settings()

# Fallbacks for local dev so the app still starts if .env isn’t defined yet.
SECRET_KEY: str = settings.JWT_SECRET or "super-secret-change-me"
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.JWT_EXPIRE_MINUTES or 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])


# ─────────────────────────────────────────────────────────────────────────────
# Pydantic schemas
# ─────────────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None  # email (subject)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] | None = None

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr = Field(..., examples=["alice@example.com"])
    password: str = Field(..., min_length=8)
    full_name: Optional[str] | None = None


# ─────────────────────────────────────────────────────────────────────────────
# DB dependency
# ─────────────────────────────────────────────────────────────────────────────

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────────────
# Password hashing utilities
# ─────────────────────────────────────────────────────────────────────────────

def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> bytes:
    return pwd_context.hash(password).encode("utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# Authentication helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    data: dict[str, str | int], expires_delta: int | None = None
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=expires_delta or ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ─────────────────────────────────────────────────────────────────────────────
# Dependencies
# ─────────────────────────────────────────────────────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(sub=email)
    except JWTError as exc:
        log.debug("JWT decode failed: %s", exc)
        raise credentials_exception from exc

    user = get_user_by_email(db, email=token_data.sub)
    if user is None:
        raise credentials_exception
    return user


# ─────────────────────────────────────────────────────────────────────────────
# Route handlers
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """Create a new user account."""
    if get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log.info("Created user %s", user.email)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate user & return an access token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.email})
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Return the current authenticated user."""
    return current_user
