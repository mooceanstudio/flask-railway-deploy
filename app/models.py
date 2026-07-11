"""Database models for the feedback board."""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .extensions import db


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Feedback(db.Model):
    """A single public feedback/guestbook entry."""

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )

    def to_dict(self) -> dict:
        """Serialise the entry for the JSON API."""
        return {
            "id": self.id,
            "name": self.name,
            "message": self.message,
            "created_at": self.created_at.isoformat()
            if self.created_at
            else None,
        }

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"<Feedback id={self.id} name={self.name!r}>"
