from uuid import UUID

from fastapi import APIRouter, Request

from app.dependencies import CurrentUser, DbSession
from app.schemas.payment import PaymentComplete, PaymentResponse, PaymentUpdate, PaymentUpdateAmount
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["payments"])


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID, db: DbSession, current_user: CurrentUser
) -> PaymentResponse:
    svc = PaymentService(db, current_user)
    payment = await svc.get(payment_id)
    return PaymentResponse.model_validate(payment)


@router.post("/{payment_id}/complete", response_model=PaymentResponse)
async def complete_payment(
    payment_id: UUID,
    data: PaymentComplete,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> PaymentResponse:
    svc = PaymentService(db, current_user, _get_ip(request))
    payment = await svc.complete(payment_id, data)
    return PaymentResponse.model_validate(payment)


@router.put("/{payment_id}/amount", response_model=PaymentResponse)
async def update_payment_amount(
    payment_id: UUID,
    data: PaymentUpdateAmount,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> PaymentResponse:
    svc = PaymentService(db, current_user, _get_ip(request))
    payment = await svc.update_amount(payment_id, data)
    return PaymentResponse.model_validate(payment)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: UUID,
    data: PaymentUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> PaymentResponse:
    """Update payment details (amount, status, dates, references).

    Allows editing all payments regardless of status.
    All fields are optional - only provided fields will be updated.
    """
    svc = PaymentService(db, current_user, _get_ip(request))
    payment = await svc.update(payment_id, data)
    return PaymentResponse.model_validate(payment)
