from uuid import UUID

from pydantic import BaseModel, Field


class SiteCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    address: str | None = None
    description: str | None = None
    monthly_base_price: int = Field(..., ge=0)
    daily_base_price: int = Field(..., ge=0)


class SiteUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    address: str | None = None
    description: str | None = None
    monthly_base_price: int | None = Field(None, ge=0)
    daily_base_price: int | None = Field(None, ge=0)


class SiteResponse(BaseModel):
    id: UUID
    name: str
    address: str | None
    description: str | None
    monthly_base_price: int
    daily_base_price: int
    space_count: int = 0

    model_config = {"from_attributes": True}
