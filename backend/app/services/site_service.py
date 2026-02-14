from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.models.site import Site
from app.models.space import Space
from app.schemas.site import SiteCreate, SiteUpdate
from app.services.audit_logger import AuditLogger
from app.utils.errors import DuplicateError, NotFoundError


class SiteService:
    def __init__(self, db: AsyncSession, user: AdminUser, ip: str | None = None) -> None:
        self.db = db
        self.user = user
        self.ip = ip
        self.audit = AuditLogger(db)

    async def list(self) -> list[Site]:
        result = await self.db.execute(
            select(Site).order_by(Site.name)
        )
        return list(result.scalars().all())

    async def get(self, site_id: UUID) -> Site:
        result = await self.db.execute(select(Site).where(Site.id == site_id))
        site = result.scalar_one_or_none()
        if site is None:
            raise NotFoundError("停車場")
        return site

    async def get_space_count(self, site_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Space).where(Space.site_id == site_id)
        )
        return result.scalar_one()

    async def create(self, data: SiteCreate) -> Site:
        # Check duplicate name
        existing = await self.db.execute(
            select(Site).where(Site.name == data.name)
        )
        if existing.scalar_one_or_none():
            raise DuplicateError("停車場", "名稱")

        site = Site(**data.model_dump())
        self.db.add(site)
        await self.db.flush()

        await self.audit.log_create(
            table_name="sites",
            record_id=site.id,
            new_values=data.model_dump(),
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return site

    async def update(self, site_id: UUID, data: SiteUpdate) -> Site:
        site = await self.get(site_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return site

        # Check name uniqueness if changing name
        if "name" in update_data and update_data["name"] != site.name:
            existing = await self.db.execute(
                select(Site).where(Site.name == update_data["name"])
            )
            if existing.scalar_one_or_none():
                raise DuplicateError("停車場", "名稱")

        old_values = {k: getattr(site, k) for k in update_data}
        for key, value in update_data.items():
            setattr(site, key, value)

        await self.db.flush()
        await self.audit.log_update(
            table_name="sites",
            record_id=site.id,
            old_values=old_values,
            new_values=update_data,
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return site

    async def delete(self, site_id: UUID) -> None:
        site = await self.get(site_id)

        # Check if site has spaces
        space_count = await self.get_space_count(site_id)
        if space_count > 0:
            from app.utils.errors import BusinessError
            raise BusinessError(f"無法刪除：此停車場仍有 {space_count} 個車位")

        old_values = {"name": site.name, "address": site.address}
        await self.db.delete(site)
        await self.db.flush()

        await self.audit.log_delete(
            table_name="sites",
            record_id=site_id,
            old_values=old_values,
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
