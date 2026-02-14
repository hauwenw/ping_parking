from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class PaymentComplete(BaseModel):
    payment_date: date
    bank_reference: str = Field(..., min_length=1, max_length=100)
    notes: str | None = None


class PaymentUpdateAmount(BaseModel):
    amount: int = Field(..., ge=0)
    notes: str = Field(..., min_length=1)


class PaymentResponse(BaseModel):
    id: UUID
    agreement_id: UUID
    amount: int
    status: str
    payment_date: date | None
    bank_reference: str | None
    notes: str | None

    model_config = {"from_attributes": True}
