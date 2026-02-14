from uuid import UUID

from pydantic import BaseModel, Field


class SpaceCreate(BaseModel):
    site_id: UUID
    name: str = Field(..., min_length=1, max_length=50)
    tags: list[str] = Field(default_factory=list)
    custom_price: int | None = Field(None, ge=0)


class SpaceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    tags: list[str] | None = None
    custom_price: int | None = Field(None, ge=0)
    status: str | None = Field(None, pattern=r"^(available|occupied|reserved|maintenance)$")


class SpaceResponse(BaseModel):
    id: UUID
    site_id: UUID
    name: str
    status: str
    tags: list[str]
    custom_price: int | None
    site_name: str | None = None
    # Computed pricing fields
    effective_monthly_price: int | None = None
    effective_daily_price: int | None = None
    price_tier: str | None = None  # "site", "tag", "custom"
    price_tag_name: str | None = None

    model_config = {"from_attributes": True}
