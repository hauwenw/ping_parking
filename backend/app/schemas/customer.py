from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.validators import validate_taiwan_phone


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=10, max_length=10)
    contact_phone: str | None = Field(None, min_length=10, max_length=10)
    email: EmailStr | None = None
    notes: str | None = None

    @field_validator("phone", "contact_phone")
    @classmethod
    def check_phone(cls, v: str | None) -> str | None:
        if v is not None:
            validate_taiwan_phone(v)
        return v


class CustomerUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    phone: str | None = Field(None, min_length=10, max_length=10)
    contact_phone: str | None = Field(None, min_length=10, max_length=10)
    email: EmailStr | None = None
    notes: str | None = None

    @field_validator("phone", "contact_phone")
    @classmethod
    def check_phone(cls, v: str | None) -> str | None:
        if v is not None:
            validate_taiwan_phone(v)
        return v


class CustomerResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    contact_phone: str | None
    email: str | None
    notes: str | None
    active_agreement_count: int = 0

    model_config = {"from_attributes": True}
