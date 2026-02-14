from fastapi import APIRouter

from app.api import agreements, auth, customers, health, payments, sites, spaces, tags

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(sites.router)
api_router.include_router(tags.router)
api_router.include_router(spaces.router)
api_router.include_router(customers.router)
api_router.include_router(agreements.router)
api_router.include_router(payments.router)

# Include health at root level (no /api/v1 prefix)
root_router = APIRouter()
root_router.include_router(health.router)
