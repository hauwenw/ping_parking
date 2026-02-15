from uuid import UUID

from sqlalchemy import ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Space(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "spaces"

    __table_args__ = (UniqueConstraint("site_id", "name", name="uq_spaces_site_id_name"),)

    site_id: Mapped[UUID] = mapped_column(ForeignKey("sites.id"), index=True)
    name: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        String(20), default="available"
    )  # available, occupied, reserved, maintenance
    tags: Mapped[list[str] | None] = mapped_column(JSON, default=list)
    custom_price: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    site: Mapped["Site"] = relationship(back_populates="spaces")  # noqa: F821
    agreements: Mapped[list["Agreement"]] = relationship(  # noqa: F821
        back_populates="space"
    )

    def __repr__(self) -> str:
        return f"Space(id={self.id!r}, name={self.name!r})"
