from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate
from app.services.audit_logger import AuditLogger
from app.utils.errors import DuplicateError, NotFoundError


class TagService:
    def __init__(self, db: AsyncSession, user: AdminUser, ip: str | None = None) -> None:
        self.db = db
        self.user = user
        self.ip = ip
        self.audit = AuditLogger(db)

    async def list(self) -> list[Tag]:
        result = await self.db.execute(select(Tag).order_by(Tag.name))
        return list(result.scalars().all())

    async def get(self, tag_id: UUID) -> Tag:
        result = await self.db.execute(select(Tag).where(Tag.id == tag_id))
        tag = result.scalar_one_or_none()
        if tag is None:
            raise NotFoundError("標籤")
        return tag

    async def create(self, data: TagCreate) -> Tag:
        existing = await self.db.execute(
            select(Tag).where(Tag.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise DuplicateError("標籤", "名稱")

        tag = Tag(**data.model_dump())
        self.db.add(tag)
        await self.db.flush()

        await self.audit.log_create(
            table_name="tags",
            record_id=tag.id,
            new_values=data.model_dump(),
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return tag

    async def update(self, tag_id: UUID, data: TagUpdate) -> Tag:
        tag = await self.get(tag_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return tag

        if "name" in update_data and update_data["name"] != tag.name:
            existing = await self.db.execute(
                select(Tag).where(Tag.name == update_data["name"])
            )
            if existing.scalar_one_or_none():
                raise DuplicateError("標籤", "名稱")

        old_values = {k: getattr(tag, k) for k in update_data}
        for key, value in update_data.items():
            setattr(tag, key, value)

        await self.db.flush()
        await self.audit.log_update(
            table_name="tags",
            record_id=tag.id,
            old_values=old_values,
            new_values=update_data,
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return tag

    async def delete(self, tag_id: UUID) -> None:
        tag = await self.get(tag_id)
        old_values = {"name": tag.name, "color": tag.color}
        await self.db.delete(tag)
        await self.db.flush()

        await self.audit.log_delete(
            table_name="tags",
            record_id=tag_id,
            old_values=old_values,
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
