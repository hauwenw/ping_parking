from uuid import UUID

from fastapi import APIRouter, Request

from app.dependencies import CurrentUser, DbSession
from app.schemas.site import SiteCreate, SiteResponse, SiteUpdate
from app.services.site_service import SiteService

router = APIRouter(prefix="/sites", tags=["sites"])


def _get_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


@router.get("", response_model=list[SiteResponse])
async def list_sites(db: DbSession, current_user: CurrentUser) -> list[SiteResponse]:
    svc = SiteService(db, current_user)
    sites = await svc.list()
    results = []
    for site in sites:
        count = await svc.get_space_count(site.id)
        results.append(SiteResponse(
            id=site.id,
            name=site.name,
            address=site.address,
            description=site.description,
            monthly_base_price=site.monthly_base_price,
            daily_base_price=site.daily_base_price,
            space_count=count,
        ))
    return results


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: UUID, db: DbSession, current_user: CurrentUser
) -> SiteResponse:
    svc = SiteService(db, current_user)
    site = await svc.get(site_id)
    count = await svc.get_space_count(site.id)
    return SiteResponse(
        id=site.id,
        name=site.name,
        address=site.address,
        description=site.description,
        monthly_base_price=site.monthly_base_price,
        daily_base_price=site.daily_base_price,
        space_count=count,
    )


@router.post("", response_model=SiteResponse, status_code=201)
async def create_site(
    data: SiteCreate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteResponse:
    svc = SiteService(db, current_user, _get_ip(request))
    site = await svc.create(data)
    return SiteResponse(
        id=site.id,
        name=site.name,
        address=site.address,
        description=site.description,
        monthly_base_price=site.monthly_base_price,
        daily_base_price=site.daily_base_price,
        space_count=0,
    )


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: UUID,
    data: SiteUpdate,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> SiteResponse:
    svc = SiteService(db, current_user, _get_ip(request))
    site = await svc.update(site_id, data)
    count = await svc.get_space_count(site.id)
    return SiteResponse(
        id=site.id,
        name=site.name,
        address=site.address,
        description=site.description,
        monthly_base_price=site.monthly_base_price,
        daily_base_price=site.daily_base_price,
        space_count=count,
    )


@router.delete("/{site_id}", status_code=204)
async def delete_site(
    site_id: UUID,
    request: Request,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    svc = SiteService(db, current_user, _get_ip(request))
    await svc.delete(site_id)
