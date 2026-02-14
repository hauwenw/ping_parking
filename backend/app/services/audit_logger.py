from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.models.system_log import SystemLog


class AuditLogger:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log(
        self,
        action: str,
        user: AdminUser | None = None,
        table_name: str | None = None,
        record_id: UUID | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str | None = None,
        batch_id: UUID | None = None,
        metadata: dict | None = None,
    ) -> SystemLog:
        log_entry = SystemLog(
            user_id=user.id if user else None,
            action=action,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            batch_id=batch_id,
            metadata_=metadata,
        )
        self.db.add(log_entry)
        await self.db.flush()
        return log_entry

    async def log_create(
        self,
        table_name: str,
        record_id: UUID,
        new_values: dict,
        user: AdminUser,
        ip_address: str | None = None,
    ) -> SystemLog:
        return await self.log(
            action="CREATE",
            user=user,
            table_name=table_name,
            record_id=record_id,
            new_values=new_values,
            ip_address=ip_address,
        )

    async def log_update(
        self,
        table_name: str,
        record_id: UUID,
        old_values: dict,
        new_values: dict,
        user: AdminUser,
        ip_address: str | None = None,
    ) -> SystemLog:
        return await self.log(
            action="UPDATE",
            user=user,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )

    async def log_delete(
        self,
        table_name: str,
        record_id: UUID,
        old_values: dict,
        user: AdminUser,
        ip_address: str | None = None,
    ) -> SystemLog:
        return await self.log(
            action="DELETE",
            user=user,
            table_name=table_name,
            record_id=record_id,
            old_values=old_values,
            ip_address=ip_address,
        )
