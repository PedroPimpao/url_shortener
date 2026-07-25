from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from .url import URL

class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    password_reset_otp: Mapped[str | None] = mapped_column(
        String(6),
        nullable=True,
    )

    password_reset_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    is_password_reset_authorized: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    urls: Mapped[list["URL"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
