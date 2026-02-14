from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class AdminUser(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "admin_users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    display_name: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"AdminUser(id={self.id!r}, email={self.email!r})"
