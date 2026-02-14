from uuid import UUID

from fastapi import APIRouter, Query, Request

from pydantic import BaseModel
from sqlalchemy import func, select

from app.dependencies import CurrentUser, DbSession
from app.models.agreement import Agreement
from app.models.payment import Payment
from app.models.space import Space
from app.schemas.agreement import (
    AgreementCreate,
    AgreementResponse,
    AgreementTerminate,
)
from app.schemas.payment import PaymentResponse
from app.services.agreement_service import AgreementService
from app.services.payment_service import PaymentService
from app.utils.crypto import decrypt_license_plate


class AgreementSummary(BaseModel):
    active_count: int
    pending_payment_total: int
    available_space_count: int
    overdue_count: int

router = APIRouter(prefix="/agreements", tags=["agreements"])


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _to_response(a) -> AgreementResponse:
    # Decrypt license plates for display
    try:
        plates = decrypt_license_plate(a.license_plates)
    except (ValueError, Exception):
        plates = "[已加密]"  # Never expose raw ciphertext on decrypt failure

    return AgreementResponse(
        id=a.id,
        customer_id=a.customer_id,
        space_id=a.space_id,
        agreement_type=a.agreement_type,
        start_date=a.start_date,
        end_date=a.end_date,
        price=a.price,
        license_plates=plates,
        notes=a.notes,
        terminated_at=str(a.terminated_at) if a.terminated_at else None,
        termination_reason=a.termination_reason,
        customer_name=a.customer.name if a.customer else None,
        space_name=a.space.name if a.space else None,
        payment_status=a.payment.status if a.payment else None,
    )


@router.get("", response_model=list[AgreementResponse])
async def list_agreements(
    db: DbSession,
    current_user: CurrentUser,
    customer_id: UUID | None = Query(None),
    space_id: UUID | None = Query(None),
    active_only: bool = Query(False),
) -> list[AgreementResponse]:
    svc = AgreementService(db, current_user)
    agreements = await svc.list(
        customer_id=customer_id, space_id=space_id, active_only=active_only
    )
    return [_to_response(a) for a in agreements]


@router.get("/summary", response_model=AgreementSummary)
async def get_agreement_summary(
    db: DbSession, current_user: CurrentUser
) -> AgreementSummary:
    from datetime import date as date_type

    # Active agreements count
    active_result = await db.execute(
        select(func.count()).select_from(Agreement).where(
            Agreement.terminated_at.is_(None)
        )
    )
    active_count = active_result.scalar_one()

    # Pending payment total
    pending_result = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == "pending"
        )
    )
    pending_payment_total = pending_result.scalar_one()

    # Available spaces
    available_result = await db.execute(
        select(func.count()).select_from(Space).where(
            Space.status == "available"
        )
    )
    available_space_count = available_result.scalar_one()

    # Overdue: active agreements past end_date with pending payment
    today = date_type.today()
    overdue_result = await db.execute(
        select(func.count()).select_from(Agreement).join(
            Payment, Payment.agreement_id == Agreement.id
        ).where(
            Agreement.terminated_at.is_(None),
            Agreement.end_date < today,
            Payment.status == "pending",
        )
    )
    overdue_count = overdue_result.scalar_one()

    return AgreementSummary(
        active_count=active_count,
        pending_payment_total=pending_payment_total,
        available_space_count=available_space_count,
        overdue_count=overdue_count,
    )


@router.get("/{agreement_id}", response_model=AgreementResponse)
async def get_agreement(
    agreement_id: UUID, db: DbSession, current_user: CurrentUser
) -> AgreementResponse:
    svc = AgreementService(db, current_user)
    agreement = await svc.get(agreement_id)
    return _to_response(agreement)


@router.post("", response_model=AgreementResponse, status_code=201)
async def create_agreement(
    data: AgreementCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> AgreementResponse:
    svc = AgreementService(db, current_user, _get_ip(request))
    agreement = await svc.create(data)
    return _to_response(agreement)


@router.post("/{agreement_id}/terminate", response_model=AgreementResponse)
async def terminate_agreement(
    agreement_id: UUID,
    data: AgreementTerminate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> AgreementResponse:
    svc = AgreementService(db, current_user, _get_ip(request))
    agreement = await svc.terminate(agreement_id, data)
    return _to_response(agreement)


@router.get("/{agreement_id}/payment", response_model=PaymentResponse)
async def get_agreement_payment(
    agreement_id: UUID, db: DbSession, current_user: CurrentUser
) -> PaymentResponse:
    svc = PaymentService(db, current_user)
    payment = await svc.get_by_agreement(agreement_id)
    return PaymentResponse.model_validate(payment)
