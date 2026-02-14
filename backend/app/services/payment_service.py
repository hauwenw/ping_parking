from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.admin_user import AdminUser
from app.models.payment import Payment
from app.schemas.payment import PaymentComplete, PaymentUpdateAmount
from app.services.audit_logger import AuditLogger
from app.utils.errors import BusinessError, NotFoundError


class PaymentService:
    def __init__(self, db: AsyncSession, user: AdminUser, ip: str | None = None) -> None:
        self.db = db
        self.user = user
        self.ip = ip
        self.audit = AuditLogger(db)

    async def get(self, payment_id: UUID) -> Payment:
        result = await self.db.execute(
            select(Payment).where(Payment.id == payment_id)
        )
        payment = result.scalar_one_or_none()
        if payment is None:
            raise NotFoundError("付款紀錄")
        return payment

    async def get_by_agreement(self, agreement_id: UUID) -> Payment:
        result = await self.db.execute(
            select(Payment).where(Payment.agreement_id == agreement_id)
        )
        payment = result.scalar_one_or_none()
        if payment is None:
            raise NotFoundError("付款紀錄")
        return payment

    async def complete(self, payment_id: UUID, data: PaymentComplete) -> Payment:
        payment = await self.get(payment_id)

        if payment.status != "pending":
            raise BusinessError(f"只有待付款狀態可以完成付款，目前狀態：{payment.status}")

        old_values = {"status": payment.status, "payment_date": None, "bank_reference": None}
        payment.status = "completed"
        payment.payment_date = data.payment_date
        payment.bank_reference = data.bank_reference
        if data.notes:
            payment.notes = data.notes

        await self.db.flush()
        await self.audit.log_update(
            table_name="payments",
            record_id=payment.id,
            old_values=old_values,
            new_values={
                "status": "completed",
                "payment_date": str(data.payment_date),
                "bank_reference": data.bank_reference,
            },
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return payment

    async def update_amount(self, payment_id: UUID, data: PaymentUpdateAmount) -> Payment:
        payment = await self.get(payment_id)

        if payment.status != "pending":
            raise BusinessError("只有待付款狀態可以修改金額")

        old_values = {"amount": payment.amount}
        payment.amount = data.amount
        payment.notes = data.notes

        await self.db.flush()
        await self.audit.log_update(
            table_name="payments",
            record_id=payment.id,
            old_values=old_values,
            new_values={"amount": data.amount, "notes": data.notes},
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return payment
