from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.dependencies import CurrentUser, DbSession
from app.models.space import Space
from app.schemas.space import SpaceCreate, SpaceResponse, SpaceUpdate
from app.services.space_service import SpaceService

router = APIRouter(prefix="/spaces", tags=["spaces"])


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _to_response(s: Space) -> SpaceResponse:
    return SpaceResponse(
        id=s.id,
        site_id=s.site_id,
        name=s.name,
        status=s.status,
        tags=s.tags or [],
        custom_price=s.custom_price,
        site_name=s.site.name if s.site else None,
    )


@router.get("", response_model=list[SpaceResponse])
async def list_spaces(
    db: DbSession,
    current_user: CurrentUser,
    site_id: UUID | None = Query(None),
) -> list[SpaceResponse]:
    svc = SpaceService(db, current_user)
    spaces = await svc.list(site_id=site_id)
    return [_to_response(s) for s in spaces]


@router.get("/{space_id}", response_model=SpaceResponse)
async def get_space(
    space_id: UUID, db: DbSession, current_user: CurrentUser
) -> SpaceResponse:
    svc = SpaceService(db, current_user)
    space = await svc.get(space_id)
    return _to_response(space)


@router.post("", response_model=SpaceResponse, status_code=201)
async def create_space(
    data: SpaceCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> SpaceResponse:
    svc = SpaceService(db, current_user, _get_ip(request))
    space = await svc.create(data)
    # Re-fetch with site relationship loaded
    space = await svc.get(space.id)
    return _to_response(space)


@router.put("/{space_id}", response_model=SpaceResponse)
async def update_space(
    space_id: UUID,
    data: SpaceUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> SpaceResponse:
    svc = SpaceService(db, current_user, _get_ip(request))
    space = await svc.update(space_id, data)
    # Re-fetch with site relationship loaded
    space = await svc.get(space.id)
    return _to_response(space)


@router.delete("/{space_id}", status_code=204)
async def delete_space(
    space_id: UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    svc = SpaceService(db, current_user, _get_ip(request))
    await svc.delete(space_id)
