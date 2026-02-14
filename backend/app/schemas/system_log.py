from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SystemLogResponse(BaseModel):
    id: UUID
    user_id: UUID | None
    action: str
    table_name: str | None
    record_id: UUID | None
    old_values: dict | None
    new_values: dict | None
    ip_address: str | None
    batch_id: UUID | None
    metadata_: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
