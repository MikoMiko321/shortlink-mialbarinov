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
    print("COOKIE SESSION:", data)
    print("CURRENT_USER:", current_user)
    print("USER_ID:", current_user.id if current_user else None)
    link = create_link(
        db,
        data.original_url,
        data.custom_alias,
        data.expires_at,
        user_id=current_user.id if current_user else None,
    )
    return {"short_code": link.short_code}


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
    return [{"short_code": link.short_code, "original_url": link.original_url} for link in links]


@links_router.get("/{short_code}/stats")
def stats(
    short_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    link = get_stats(
        db,
        short_code,
        user_id=current_user.id if current_user else None,
    )

    if not link:
        raise HTTPException(status_code=404)

    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "clicks": link.clicks,
        "last_accessed": link.last_accessed,
    }


@links_router.put("/{short_code}")
def update(
    short_code: str,
    data: LinkUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    link = update_link(
        db,
        short_code,
        data.original_url,
        user_id=current_user.id if current_user else None,
    )

    if not link:
        raise HTTPException(status_code=404)

    return {"status": "updated"}


@links_router.delete("/{short_code}")
def delete(
    short_code: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional),
):
    ok = delete_link(
        db,
        short_code,
        user_id=current_user.id if current_user else None,
    )

    if not ok:
        raise HTTPException(status_code=404)

    return {"status": "deleted"}


@redirect_router.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    url = get_original_url(db, short_code)

    if not url:
        raise HTTPException(status_code=404)

    return RedirectResponse(url)
