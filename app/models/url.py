from datetime import datetime
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .user import User

class URL(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "urls"

    def __init__(self, title, original_url, short_code, user_id):
        self.title = title
        self.original_url = original_url
        self.short_code = short_code
        self.user_id = user_id
        # self.short_url = f'url_site/{short_code}'

    original_url: Mapped[str] = mapped_column(
        String(2048),
        nullable=False,
    )

    short_code: Mapped[str] = mapped_column(
        String(8),
        unique=True,
        index=True,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    clicks: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="urls",
        lazy="selectin",
    )
