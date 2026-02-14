from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Customer(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("name", "phone", name="uq_customer_name_phone"),
    )

    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(10), index=True)
    contact_phone: Mapped[str | None] = mapped_column(String(10))
    email: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    agreements: Mapped[list["Agreement"]] = relationship(  # noqa: F821
        back_populates="customer"
    )

    def __repr__(self) -> str:
        return f"Customer(id={self.id!r}, name={self.name!r})"
