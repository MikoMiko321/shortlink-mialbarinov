from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.auth.service import get_current_user_optional
from app.database import get_db
from app.models.link import Link
from app.schemas.link import LinkCreate, LinkUpdate
from app.services.link_service import (
    create_link,
    delete_link,
    delete_unused,
    get_stats,
    search_by_original,
    update_link,
)

links_router = APIRouter(prefix="/links")
redirect_router = APIRouter()


@links_router.post("/shorten")
def shorten(
    data: LinkCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    link = create_link(
        db,
        data.original_url,
        data.custom_alias,
        data.expires_at,
        user_id=current_user.id if current_user else None,
    )

    code = link.custom_alias or link.short_code

    return {"short_code": code}


@links_router.delete("/cleanup")
def cleanup(days: int = 30, db: Session = Depends(get_db)):
    delete_unused(db, days)
    return {"status": "cleanup done"}


@links_router.get("/search")
def search(
    fragment: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    links = search_by_original(
        db,
        fragment,
        user_id=current_user.id if current_user else None,
    )

    result = []

    for link in links:
        code = link.custom_alias or link.short_code
        result.append(
            {
                "short_code": code,
                "original_url": link.original_url,
            }
        )

    return result


@links_router.get("/{code}/stats")
def stats(
    code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    link = db.scalar(
        select(Link).where(
            or_(
                Link.short_code == code,
                Link.custom_alias == code,
            )
        )
    )

    if not link:
        raise HTTPException(status_code=404)

    if current_user and link.user_id != current_user.id:
        raise HTTPException(status_code=404)

    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "clicks": link.clicks,
        "last_accessed": link.last_accessed,
    }


@links_router.put("/{code}")
def update(
    code: str,
    data: LinkUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    link = update_link(
        db,
        code,
        data.original_url,
        user_id=current_user.id if current_user else None,
    )

    if not link:
        raise HTTPException(status_code=404)

    return {"status": "updated"}


@links_router.delete("/{code}")
def delete(
    code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    ok = delete_link(
        db,
        code,
        user_id=current_user.id if current_user else None,
    )

    if not ok:
        raise HTTPException(status_code=404)

    return {"status": "deleted"}


@redirect_router.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    link = db.scalar(
        select(Link).where(
            or_(
                Link.short_code == code,
                Link.custom_alias == code,
            )
        )
    )

    if not link:
        raise HTTPException(status_code=404)

    return RedirectResponse(link.original_url)
