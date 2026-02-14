from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


class SystemLog(UUIDMixin, Base):
    """Immutable audit log. No updated_at by design."""

    __tablename__ = "system_logs"

    user_id: Mapped[UUID | None] = mapped_column(index=True)
    action: Mapped[str] = mapped_column(String(20), index=True)
    table_name: Mapped[str | None] = mapped_column(String(50), index=True)
    record_id: Mapped[UUID | None] = mapped_column(index=True)
    old_values: Mapped[dict | None] = mapped_column(JSON)
    new_values: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(Text)
    batch_id: Mapped[UUID | None] = mapped_column(index=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    def __repr__(self) -> str:
        return f"SystemLog(id={self.id!r}, action={self.action!r})"
