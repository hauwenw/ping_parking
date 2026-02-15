from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.dependencies import CurrentUser, DbSession
from app.models.space import Space
from app.models.tag import Tag
from app.schemas.space import SpaceBatchCreate, SpaceCreate, SpaceResponse, SpaceUpdate
from app.services.space_service import SpaceService

router = APIRouter(prefix="/spaces", tags=["spaces"])


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def _to_response(s: Space, all_tags: list[Tag] | None = None, svc: SpaceService | None = None) -> SpaceResponse:
    resp = SpaceResponse(
        id=s.id,
        site_id=s.site_id,
        name=s.name,
        status=s.status,
        tags=s.tags or [],
        custom_price=s.custom_price,
        site_name=s.site.name if s.site else None,
    )
    if svc and all_tags is not None:
        pricing = svc.compute_pricing(s, all_tags)
        resp.effective_monthly_price = pricing["monthly"]
        resp.effective_daily_price = pricing["daily"]
        resp.price_tier = pricing["tier"]
        resp.price_tag_name = pricing.get("tag_name")
    return resp


@router.get("", response_model=list[SpaceResponse])
async def list_spaces(
    db: DbSession,
    current_user: CurrentUser,
    site_id: UUID | None = Query(None),
    status: str | None = Query(None),
    tag: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[SpaceResponse]:
    svc = SpaceService(db, current_user)
    spaces = await svc.list(site_id=site_id, status=status, tag=tag, offset=offset, limit=limit)
    all_tags = await svc.get_all_tags()
    return [_to_response(s, all_tags, svc) for s in spaces]


@router.post("/batch", response_model=list[SpaceResponse], status_code=201)
async def batch_create_spaces(
    data: SpaceBatchCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> list[SpaceResponse]:
    svc = SpaceService(db, current_user, _get_ip(request))
    spaces = await svc.batch_create(data)
    # Re-fetch with site relationships loaded
    all_tags = await svc.get_all_tags()
    result = []
    for space in spaces:
        loaded = await svc.get(space.id)
        result.append(_to_response(loaded, all_tags, svc))
    return result


@router.get("/{space_id}", response_model=SpaceResponse)
async def get_space(
    space_id: UUID, db: DbSession, current_user: CurrentUser
) -> SpaceResponse:
    svc = SpaceService(db, current_user)
    space = await svc.get(space_id)
    all_tags = await svc.get_all_tags()
    return _to_response(space, all_tags, svc)


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
    all_tags = await svc.get_all_tags()
    return _to_response(space, all_tags, svc)


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
    all_tags = await svc.get_all_tags()
    return _to_response(space, all_tags, svc)


@router.delete("/{space_id}", status_code=204)
async def delete_space(
    space_id: UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    svc = SpaceService(db, current_user, _get_ip(request))
    await svc.delete(space_id)
