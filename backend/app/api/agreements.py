from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.dependencies import CurrentUser, DbSession
from app.schemas.agreement import (
    AgreementCreate,
    AgreementResponse,
    AgreementTerminate,
)
from app.schemas.payment import PaymentResponse
from app.services.agreement_service import AgreementService
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/agreements", tags=["agreements"])


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _to_response(a) -> AgreementResponse:
    return AgreementResponse(
        id=a.id,
        customer_id=a.customer_id,
        space_id=a.space_id,
        agreement_type=a.agreement_type,
        start_date=a.start_date,
        end_date=a.end_date,
        price=a.price,
        license_plates=a.license_plates,
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
