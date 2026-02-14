from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Site(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "sites"

    name: Mapped[str] = mapped_column(String(100), unique=True)
    address: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    monthly_base_price: Mapped[int] = mapped_column(Integer, default=0)
    daily_base_price: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    spaces: Mapped[list["Space"]] = relationship(  # noqa: F821
        back_populates="site", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Site(id={self.id!r}, name={self.name!r})"
