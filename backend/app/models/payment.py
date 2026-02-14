from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Payment(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "payments"

    agreement_id: Mapped[UUID] = mapped_column(
        ForeignKey("agreements.id"), unique=True, index=True
    )
    amount: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String(20), default="pending"
    )  # pending, completed, voided
    payment_date: Mapped[date | None] = mapped_column(Date)
    bank_reference: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    agreement: Mapped["Agreement"] = relationship(  # noqa: F821
        back_populates="payment"
    )

    def __repr__(self) -> str:
        return f"Payment(id={self.id!r}, status={self.status!r})"
