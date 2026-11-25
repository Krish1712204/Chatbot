"""Password hashing, JWT tokens and the "who is logged in?" dependency."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import User, get_db

ALGORITHM = "HS256"
TOKEN_DAYS = 7


# ---------- passwords ----------

def hash_password(password: str) -> str:
    # gensalt() adds random "salt", so two users with the same password get different hashes.
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except ValueError:  # bcrypt rejects passwords over 72 bytes; such a password can't match
        return False


# ---------- tokens ----------

def create_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),  # "subject": who this token belongs to (JWT wants a string)
        "exp": datetime.now(timezone.utc) + timedelta(days=TOKEN_DAYS),  # expiry time
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def read_token(token: str) -> int | None:
    """Return the user id inside a valid token, or None if it is fake, changed or expired."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        return None


# ---------- dependency ----------

# Reads the "Authorization: Bearer <token>" header. auto_error=False lets us send our own message.
bearer = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """Add `user: User = Depends(get_current_user)` to any endpoint that needs login."""
    user_id = read_token(creds.credentials) if creds else None
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in again",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
