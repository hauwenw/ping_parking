from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.models.agreement import Agreement
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.audit_logger import AuditLogger
from app.utils.errors import BusinessError, DuplicateError, NotFoundError


class CustomerService:
    def __init__(self, db: AsyncSession, user: AdminUser, ip: str | None = None) -> None:
        self.db = db
        self.user = user
        self.ip = ip
        self.audit = AuditLogger(db)

    async def list(self) -> list[Customer]:
        result = await self.db.execute(
            select(Customer).order_by(Customer.name)
        )
        return list(result.scalars().all())

    async def get(self, customer_id: UUID) -> Customer:
        result = await self.db.execute(
            select(Customer).where(Customer.id == customer_id)
        )
        customer = result.scalar_one_or_none()
        if customer is None:
            raise NotFoundError("客戶")
        return customer

    async def get_active_agreement_count(self, customer_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Agreement)
            .where(
                Agreement.customer_id == customer_id,
                Agreement.terminated_at.is_(None),
            )
        )
        return result.scalar_one()

    async def create(self, data: CustomerCreate) -> Customer:
        # Check unique constraint (name, phone)
        existing = await self.db.execute(
            select(Customer).where(
                Customer.name == data.name,
                Customer.phone == data.phone,
            )
        )
        if existing.scalar_one_or_none():
            raise DuplicateError("客戶", "姓名與電話")

        customer = Customer(**data.model_dump())
        self.db.add(customer)
        await self.db.flush()

        await self.audit.log_create(
            table_name="customers",
            record_id=customer.id,
            new_values=data.model_dump(),
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return customer

    async def update(self, customer_id: UUID, data: CustomerUpdate) -> Customer:
        customer = await self.get(customer_id)
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return customer

        # Check unique constraint if name or phone changing
        new_name = update_data.get("name", customer.name)
        new_phone = update_data.get("phone", customer.phone)
        if new_name != customer.name or new_phone != customer.phone:
            existing = await self.db.execute(
                select(Customer).where(
                    Customer.name == new_name,
                    Customer.phone == new_phone,
                    Customer.id != customer_id,
                )
            )
            if existing.scalar_one_or_none():
                raise DuplicateError("客戶", "姓名與電話")

        old_values = {k: getattr(customer, k) for k in update_data}
        for key, value in update_data.items():
            setattr(customer, key, value)

        await self.db.flush()
        await self.audit.log_update(
            table_name="customers",
            record_id=customer.id,
            old_values=old_values,
            new_values=update_data,
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return customer

    async def delete(self, customer_id: UUID) -> None:
        customer = await self.get(customer_id)

        active_count = await self.get_active_agreement_count(customer_id)
        if active_count > 0:
            raise BusinessError(f"無法刪除：此客戶仍有 {active_count} 個有效合約")

        old_values = {"name": customer.name, "phone": customer.phone}
        await self.db.delete(customer)
        await self.db.flush()

        await self.audit.log_delete(
            table_name="customers",
            record_id=customer_id,
            old_values=old_values,
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
