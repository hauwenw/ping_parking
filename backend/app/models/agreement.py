from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class Agreement(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "agreements"

    customer_id: Mapped[UUID] = mapped_column(
        ForeignKey("customers.id"), index=True
    )
    space_id: Mapped[UUID] = mapped_column(ForeignKey("spaces.id"), index=True)
    agreement_type: Mapped[str] = mapped_column(
        String(20)
    )  # daily, monthly, quarterly, yearly
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    price: Mapped[int] = mapped_column(Integer)
    license_plates: Mapped[str] = mapped_column(String(500))
    notes: Mapped[str | None] = mapped_column(Text)
    terminated_at: Mapped[datetime | None] = mapped_column()
    termination_reason: Mapped[str | None] = mapped_column(Text)

    # Relationships
    customer: Mapped["Customer"] = relationship(  # noqa: F821
        back_populates="agreements"
    )
    space: Mapped["Space"] = relationship(back_populates="agreements")  # noqa: F821
    payment: Mapped["Payment | None"] = relationship(  # noqa: F821
        back_populates="agreement", uselist=False
    )

    def __repr__(self) -> str:
        return f"Agreement(id={self.id!r}, type={self.agreement_type!r})"
