from uuid import UUID

from fastapi import APIRouter, Request

from app.dependencies import CurrentUser, DbSession
from app.schemas.tag import TagCreate, TagResponse, TagUpdate
from app.services.tag_service import TagService

router = APIRouter(prefix="/tags", tags=["tags"])


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("", response_model=list[TagResponse])
async def list_tags(db: DbSession, current_user: CurrentUser) -> list[TagResponse]:
    svc = TagService(db, current_user)
    tags = await svc.list()
    return [TagResponse.model_validate(t) for t in tags]


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: UUID, db: DbSession, current_user: CurrentUser
) -> TagResponse:
    svc = TagService(db, current_user)
    tag = await svc.get(tag_id)
    return TagResponse.model_validate(tag)


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> TagResponse:
    svc = TagService(db, current_user, _get_ip(request))
    tag = await svc.create(data)
    return TagResponse.model_validate(tag)


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: UUID,
    data: TagUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> TagResponse:
    svc = TagService(db, current_user, _get_ip(request))
    tag = await svc.update(tag_id, data)
    return TagResponse.model_validate(tag)


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    svc = TagService(db, current_user, _get_ip(request))
    await svc.delete(tag_id)
