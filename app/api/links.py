from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.link import LinkCreate, LinkUpdate
from app.services.link_service import (
    create_link,
    delete_link,
    get_original_url,
    get_stats,
    search_by_original,
    update_link,
)

router = APIRouter(prefix="/links")


@router.post("/shorten")
def shorten(data: LinkCreate, db: Session = Depends(get_db)):
    link = create_link(db, data.original_url, data.custom_alias, data.expires_at)
    return {"short_code": link.short_code}


@router.get("/{short_code}")
def redirect(short_code: str, db: Session = Depends(get_db)):
    url = get_original_url(db, short_code)

    if not url:
        raise HTTPException(404)

    return RedirectResponse(url)


@router.delete("/{short_code}")
def delete(short_code: str, db: Session = Depends(get_db)):
    ok = delete_link(db, short_code)

    if not ok:
        raise HTTPException(404)

    return {"status": "deleted"}


@router.put("/{short_code}")
def update(short_code: str, data: LinkUpdate, db: Session = Depends(get_db)):
    link = update_link(db, short_code, data.original_url)

    if not link:
        raise HTTPException(404)

    return {"status": "updated"}


@router.get("/{short_code}/stats")
def stats(short_code: str, db: Session = Depends(get_db)):
    link = get_stats(db, short_code)

    if not link:
        raise HTTPException(404)

    return {
        "original_url": link.original_url,
        "created_at": link.created_at,
        "clicks": link.clicks,
        "last_accessed": link.last_accessed,
    }


@router.get("/search")
def search(original_url: str, db: Session = Depends(get_db)):
    link = search_by_original(db, original_url)

    if not link:
        raise HTTPException(404)

    return {"short_code": link.short_code}
