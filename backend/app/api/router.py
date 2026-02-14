from fastapi import APIRouter

from app.api import auth, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)

# Include health at root level (no /api/v1 prefix)
root_router = APIRouter()
root_router.include_router(health.router)
