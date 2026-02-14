from uuid import UUID

from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    color: str = Field(..., pattern=r"^#[0-9a-fA-F]{6}$")
    description: str | None = None
    monthly_price: int | None = Field(None, ge=0)
    daily_price: int | None = Field(None, ge=0)


class TagUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=30)
    color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$")
    description: str | None = None
    monthly_price: int | None = Field(None, ge=0)
    daily_price: int | None = Field(None, ge=0)


class TagResponse(BaseModel):
    id: UUID
    name: str
    color: str
    description: str | None
    monthly_price: int | None
    daily_price: int | None

    model_config = {"from_attributes": True}
