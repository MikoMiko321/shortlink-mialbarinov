from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.service import get_current_user_optional
from app.database import get_db
from app.schemas.link import LinkCreate, LinkUpdate
from app.services.link_service import (
    create_link,
    delete_link,
    delete_unused,
    get_original_url,
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
    user_id = current_user.id if current_user else None

    link = create_link(
        db,
        data.original_url,
        data.custom_alias,
        data.expires_at,
        user_id=user_id,
    )

    code = link.custom_alias or link.short_code

    return {"short_code": code}


@links_router.delete("/cleanup")
def cleanup(
    days: int = 30,
    db: Session = Depends(get_db),
):
    delete_unused(db, days)
    return {"status": "cleanup done"}


@links_router.get("/search")
def search(
    fragment: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None

    return search_by_original(
        db,
        fragment,
        user_id=user_id,
    )


@links_router.get("/{code}/stats")
def stats(
    code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None

    link = get_stats(
        db,
        code,
        user_id=user_id,
    )

    if not link:
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
    user_id = current_user.id if current_user else None

    link = update_link(
        db,
        code,
        data.original_url,
        user_id=user_id,
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
    user_id = current_user.id if current_user else None

    ok = delete_link(
        db,
        code,
        user_id=user_id,
    )

    if not ok:
        raise HTTPException(status_code=404)

    return {"status": "deleted"}


@redirect_router.get("/{code}")
def redirect(
    code: str,
    db: Session = Depends(get_db),
):
    url = get_original_url(db, code)

    if not url:
        raise HTTPException(status_code=404)

    return RedirectResponse(url, status_code=302)
