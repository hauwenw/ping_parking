from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.admin_user import AdminUser
from app.models.site import Site
from app.models.space import Space
from app.schemas.space import SpaceCreate, SpaceUpdate
from app.services.audit_logger import AuditLogger
from app.utils.errors import BusinessError, NotFoundError


class SpaceService:
    def __init__(self, db: AsyncSession, user: AdminUser, ip: str | None = None) -> None:
        self.db = db
        self.user = user
        self.ip = ip
        self.audit = AuditLogger(db)

    async def list(self, site_id: UUID | None = None) -> list[Space]:
        stmt = select(Space).options(selectinload(Space.site))
        if site_id:
            stmt = stmt.where(Space.site_id == site_id)
        stmt = stmt.order_by(Space.name)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get(self, space_id: UUID) -> Space:
        result = await self.db.execute(
            select(Space).options(selectinload(Space.site)).where(Space.id == space_id)
        )
        space = result.scalar_one_or_none()
        if space is None:
            raise NotFoundError("車位")
        return space

    async def create(self, data: SpaceCreate) -> Space:
        # Verify site exists
        site_result = await self.db.execute(
            select(Site).where(Site.id == data.site_id)
        )
        if site_result.scalar_one_or_none() is None:
            raise NotFoundError("停車場")

        space = Space(**data.model_dump())
        self.db.add(space)
        await self.db.flush()

        await self.audit.log_create(
            table_name="spaces",
            record_id=space.id,
            new_values=data.model_dump(mode="json"),
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return space

    async def update(self, space_id: UUID, data: SpaceUpdate) -> Space:
        space = await self.get(space_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return space

        # Prevent status change to available if active agreement exists
        if "status" in update_data and update_data["status"] == "available":
            from app.models.agreement import Agreement
            active = await self.db.execute(
                select(Agreement).where(
                    Agreement.space_id == space_id,
                    Agreement.terminated_at.is_(None),
                )
            )
            if active.scalar_one_or_none():
                raise BusinessError("此車位有有效合約，無法設為可用")

        old_values = {k: getattr(space, k) for k in update_data}
        for key, value in update_data.items():
            setattr(space, key, value)

        await self.db.flush()
        await self.audit.log_update(
            table_name="spaces",
            record_id=space.id,
            old_values=old_values,
            new_values=update_data,
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return space

    async def delete(self, space_id: UUID) -> None:
        space = await self.get(space_id)

        # Check for active agreements
        from app.models.agreement import Agreement
        active = await self.db.execute(
            select(Agreement).where(
                Agreement.space_id == space_id,
                Agreement.terminated_at.is_(None),
            )
        )
        if active.scalar_one_or_none():
            raise BusinessError("無法刪除：此車位有有效合約")

        old_values = {"name": space.name, "site_id": str(space.site_id)}
        await self.db.delete(space)
        await self.db.flush()

        await self.audit.log_delete(
            table_name="spaces",
            record_id=space_id,
            old_values=old_values,
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
