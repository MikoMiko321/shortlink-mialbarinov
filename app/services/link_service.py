from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import delete, or_, select
from sqlalchemy.orm import Session

from app.cache.redis import redis_client
from app.models.link import Link
from app.utils.shortener import generate_short_code


def create_link(
    db: Session,
    original_url: str,
    custom_alias: str | None,
    expires_at,
    user_id: int | None = None,
):
    code = custom_alias or generate_short_code()

    existing = db.scalar(select(Link).where(Link.short_code == code, Link.user_id == user_id))

    if existing:
        raise HTTPException(status_code=400, detail="alias already exists")

    link = Link(
        original_url=original_url,
        short_code=code,
        custom_alias=custom_alias,
        expires_at=expires_at,
        user_id=user_id,
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


def get_original_url(db: Session, short_code: str):
    cached = redis_client.get(short_code)

    if cached:
        return cached

    link = db.scalar(select(Link).where(Link.short_code == short_code))

    if not link:
        return None

    redis_client.set(short_code, link.original_url)

    link.clicks += 1
    link.last_accessed = datetime.now(UTC)

    db.commit()

    return link.original_url


def delete_link(db: Session, short_code: str, user_id: int | None = None):
    q = select(Link).where(Link.short_code == short_code)

    if user_id is not None:
        q = q.where(Link.user_id == user_id)

    link = db.scalar(q)

    if not link:
        return False

    redis_client.delete(short_code)

    db.delete(link)
    db.commit()

    return True


def update_link(
    db: Session,
    short_code: str,
    new_url: str,
    user_id: int | None = None,
):
    q = select(Link).where(Link.short_code == short_code)

    if user_id is not None:
        q = q.where(Link.user_id == user_id)

    link = db.scalar(q)

    if not link:
        return None

    link.original_url = new_url

    db.commit()

    redis_client.delete(short_code)

    return link


def get_stats(db: Session, short_code: str, user_id: int | None = None):
    q = select(Link).where(Link.short_code == short_code)

    if user_id is not None:
        q = q.where(Link.user_id == user_id)

    return db.scalar(q)


def search_by_original(
    db: Session,
    fragment: str,
    user_id: int | None = None,
):
    if len(fragment) < 4:
        return []

    q = select(Link).where(Link.original_url.ilike(f"%{fragment}%"))

    if user_id is not None:
        q = q.where(Link.user_id == user_id)

    q = q.order_by(Link.created_at.desc())

    return db.scalars(q).all()


def delete_unused(db: Session, days: int):
    border = datetime.now(UTC) - timedelta(days=days)

    q = delete(Link).where(or_(Link.last_accessed < border, Link.last_accessed.is_(None)))

    db.execute(q)
    db.commit()
