from datetime import date, datetime
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.admin_user import AdminUser
from app.models.agreement import Agreement
from app.models.customer import Customer
from app.models.payment import Payment
from app.models.space import Space
from app.schemas.agreement import AgreementCreate, AgreementTerminate
from app.services.audit_logger import AuditLogger
from app.utils.errors import BusinessError, DoubleBookingError, NotFoundError


def _calc_end_date(start: date, agreement_type: str) -> date:
    if agreement_type == "daily":
        return start + relativedelta(days=1)
    elif agreement_type == "monthly":
        return start + relativedelta(months=1)
    elif agreement_type == "quarterly":
        return start + relativedelta(months=3)
    elif agreement_type == "yearly":
        return start + relativedelta(years=1)
    raise ValueError(f"Invalid agreement type: {agreement_type}")


class AgreementService:
    def __init__(self, db: AsyncSession, user: AdminUser, ip: str | None = None) -> None:
        self.db = db
        self.user = user
        self.ip = ip
        self.audit = AuditLogger(db)

    async def list(
        self,
        customer_id: UUID | None = None,
        space_id: UUID | None = None,
        active_only: bool = False,
    ) -> list[Agreement]:
        stmt = (
            select(Agreement)
            .options(
                selectinload(Agreement.customer),
                selectinload(Agreement.space),
                selectinload(Agreement.payment),
            )
        )
        if customer_id:
            stmt = stmt.where(Agreement.customer_id == customer_id)
        if space_id:
            stmt = stmt.where(Agreement.space_id == space_id)
        if active_only:
            stmt = stmt.where(Agreement.terminated_at.is_(None))
        stmt = stmt.order_by(Agreement.start_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get(self, agreement_id: UUID) -> Agreement:
        result = await self.db.execute(
            select(Agreement)
            .options(
                selectinload(Agreement.customer),
                selectinload(Agreement.space),
                selectinload(Agreement.payment),
            )
            .where(Agreement.id == agreement_id)
        )
        agreement = result.scalar_one_or_none()
        if agreement is None:
            raise NotFoundError("合約")
        return agreement

    async def create(self, data: AgreementCreate) -> Agreement:
        # Verify customer exists
        cust_result = await self.db.execute(
            select(Customer).where(Customer.id == data.customer_id)
        )
        if cust_result.scalar_one_or_none() is None:
            raise NotFoundError("客戶")

        # Verify space exists
        space_result = await self.db.execute(
            select(Space).where(Space.id == data.space_id)
        )
        space = space_result.scalar_one_or_none()
        if space is None:
            raise NotFoundError("車位")

        # Check for active agreement on this space (double booking)
        active_result = await self.db.execute(
            select(Agreement).where(
                Agreement.space_id == data.space_id,
                Agreement.terminated_at.is_(None),
            )
        )
        if active_result.scalar_one_or_none():
            raise DoubleBookingError(space.name)

        end_date = _calc_end_date(data.start_date, data.agreement_type)

        agreement = Agreement(
            customer_id=data.customer_id,
            space_id=data.space_id,
            agreement_type=data.agreement_type,
            start_date=data.start_date,
            end_date=end_date,
            price=data.price,
            license_plates=data.license_plates,
            notes=data.notes,
        )
        self.db.add(agreement)
        await self.db.flush()

        # Auto-generate payment record
        payment = Payment(
            agreement_id=agreement.id,
            amount=data.price,
            status="pending",
        )
        self.db.add(payment)
        await self.db.flush()

        # Update space status to occupied
        space.status = "occupied"

        await self.audit.log_create(
            table_name="agreements",
            record_id=agreement.id,
            new_values={
                "customer_id": str(data.customer_id),
                "space_id": str(data.space_id),
                "agreement_type": data.agreement_type,
                "start_date": str(data.start_date),
                "end_date": str(end_date),
                "price": data.price,
                "license_plates": data.license_plates,
            },
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()

        # Re-fetch with relationships loaded
        return await self.get(agreement.id)

    async def terminate(
        self, agreement_id: UUID, data: AgreementTerminate
    ) -> Agreement:
        agreement = await self.get(agreement_id)

        if agreement.terminated_at is not None:
            raise BusinessError("此合約已終止")

        now = datetime.now()
        agreement.terminated_at = now
        agreement.termination_reason = data.termination_reason

        # Void pending payment
        if agreement.payment and agreement.payment.status == "pending":
            agreement.payment.status = "voided"

        # Release space
        space_result = await self.db.execute(
            select(Space).where(Space.id == agreement.space_id)
        )
        space = space_result.scalar_one_or_none()
        if space:
            space.status = "available"

        await self.db.flush()
        await self.audit.log_update(
            table_name="agreements",
            record_id=agreement.id,
            old_values={"terminated_at": None, "termination_reason": None},
            new_values={
                "terminated_at": str(now),
                "termination_reason": data.termination_reason,
            },
            user=self.user,
            ip_address=self.ip,
        )
        await self.db.commit()
        return await self.get(agreement_id)
