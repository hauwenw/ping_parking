from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.dependencies import CurrentUser, DbSession
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("", response_model=list[CustomerResponse])
async def list_customers(
    db: DbSession,
    current_user: CurrentUser,
    search: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[CustomerResponse]:
    svc = CustomerService(db, current_user)
    customers = await svc.list(search=search, offset=offset, limit=limit)
    results = []
    for c in customers:
        count = await svc.get_active_agreement_count(c.id)
        results.append(CustomerResponse(
            id=c.id,
            name=c.name,
            phone=c.phone,
            contact_phone=c.contact_phone,
            email=c.email,
            notes=c.notes,
            active_agreement_count=count,
        ))
    return results


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID, db: DbSession, current_user: CurrentUser
) -> CustomerResponse:
    svc = CustomerService(db, current_user)
    customer = await svc.get(customer_id)
    count = await svc.get_active_agreement_count(customer.id)
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        phone=customer.phone,
        contact_phone=customer.contact_phone,
        email=customer.email,
        notes=customer.notes,
        active_agreement_count=count,
    )


@router.post("", response_model=CustomerResponse, status_code=201)
async def create_customer(
    data: CustomerCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> CustomerResponse:
    svc = CustomerService(db, current_user, _get_ip(request))
    customer = await svc.create(data)
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        phone=customer.phone,
        contact_phone=customer.contact_phone,
        email=customer.email,
        notes=customer.notes,
        active_agreement_count=0,
    )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> CustomerResponse:
    svc = CustomerService(db, current_user, _get_ip(request))
    customer = await svc.update(customer_id, data)
    count = await svc.get_active_agreement_count(customer.id)
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        phone=customer.phone,
        contact_phone=customer.contact_phone,
        email=customer.email,
        notes=customer.notes,
        active_agreement_count=count,
    )


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    svc = CustomerService(db, current_user, _get_ip(request))
    await svc.delete(customer_id)
