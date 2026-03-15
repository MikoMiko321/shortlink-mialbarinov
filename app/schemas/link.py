from datetime import datetime

from pydantic import BaseModel


class LinkCreate(BaseModel):
    original_url: str
    custom_alias: str | None = None
    expires_at: datetime | None = None


class LinkUpdate(BaseModel):
    original_url: str


class LinkStats(BaseModel):
    original_url: str
    created_at: datetime
    clicks: int
    last_accessed: datetime | None
