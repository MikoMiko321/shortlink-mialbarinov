import hashlib
import uuid

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.cache.redis import redis_client
from app.database import get_db


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(db: Session, login: str, password: str):
    existing = db.scalar(select(User).where(User.login == login))
    if existing:
        raise ValueError("user exists")

    user = User(login=login, password_hash=hash_password(password))

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate(db: Session, login: str, password: str):
    user = db.scalar(select(User).where(User.login == login))
    if not user:
        return None

    if user.password_hash != hash_password(password):
        return None

    return user


def create_session(user_id: int) -> str:
    session_id = str(uuid.uuid4())

    redis_client.set(f"session:{session_id}", user_id, ex=86400)

    return session_id


def get_user_by_session(session_id: str):
    user_id = redis_client.get(f"session:{session_id}")
    if not user_id:
        return None

    return int(user_id)


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
):
    session_id = request.cookies.get("session_id")

    if not session_id:
        return None

    user_id = get_user_by_session(session_id)

    if not user_id:
        return None

    return db.get(User, user_id)
