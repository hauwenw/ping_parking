from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class AgreementCreate(BaseModel):
    customer_id: UUID
    space_id: UUID
    agreement_type: str = Field(
        ..., pattern=r"^(daily|monthly|quarterly|yearly)$"
    )
    start_date: date
    price: int = Field(..., ge=0)
    license_plates: str = Field(..., min_length=1, max_length=500)
    notes: str | None = None


class AgreementTerminate(BaseModel):
    termination_reason: str = Field(..., min_length=1)


class AgreementResponse(BaseModel):
    id: UUID
    customer_id: UUID
    space_id: UUID
    agreement_type: str
    start_date: date
    end_date: date
    price: int
    license_plates: str
    notes: str | None
    terminated_at: str | None = None
    termination_reason: str | None = None
    customer_name: str | None = None
    space_name: str | None = None
    payment_status: str | None = None

    model_config = {"from_attributes": True}
