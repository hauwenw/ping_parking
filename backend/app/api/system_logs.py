from uuid import UUID

from fastapi import APIRouter, Query

from app.dependencies import CurrentUser, DbSession
from app.models.system_log import SystemLog
from app.schemas.system_log import SystemLogResponse

from sqlalchemy import select

router = APIRouter(prefix="/system-logs", tags=["system-logs"])


@router.get("", response_model=list[SystemLogResponse])
async def list_system_logs(
    db: DbSession,
    current_user: CurrentUser,
    action: str | None = Query(None),
    table_name: str | None = Query(None),
    record_id: UUID | None = Query(None),
    user_id: UUID | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> list[SystemLogResponse]:
    stmt = select(SystemLog)
    if action:
        stmt = stmt.where(SystemLog.action == action)
    if table_name:
        stmt = stmt.where(SystemLog.table_name == table_name)
    if record_id:
        stmt = stmt.where(SystemLog.record_id == record_id)
    if user_id:
        stmt = stmt.where(SystemLog.user_id == user_id)
    stmt = stmt.order_by(SystemLog.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    logs = result.scalars().all()
    return [SystemLogResponse.model_validate(log) for log in logs]


@router.get("/{log_id}", response_model=SystemLogResponse)
async def get_system_log(
    log_id: UUID, db: DbSession, current_user: CurrentUser
) -> SystemLogResponse:
    from app.utils.errors import NotFoundError

    result = await db.execute(select(SystemLog).where(SystemLog.id == log_id))
    log = result.scalar_one_or_none()
    if log is None:
        raise NotFoundError("系統紀錄")
    return SystemLogResponse.model_validate(log)
