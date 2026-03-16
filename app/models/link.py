from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    original_url: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    short_code: Mapped[str | None] = mapped_column(
        String,
        unique=True,
        nullable=True,
    )

    custom_alias: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    clicks: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    last_accessed: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=True,
    )
