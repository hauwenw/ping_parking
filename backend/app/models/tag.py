from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Tag(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(50), unique=True)
    color: Mapped[str] = mapped_column(String(7), default="#6B7280")
    description: Mapped[str | None] = mapped_column(Text)
    monthly_price: Mapped[int | None] = mapped_column(Integer)
    daily_price: Mapped[int | None] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"Tag(id={self.id!r}, name={self.name!r})"
