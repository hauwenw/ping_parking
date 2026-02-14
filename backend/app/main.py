from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router, root_router
from app.config import settings
from app.utils.errors import BusinessError, DuplicateError, NotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Refuse to start with dev-default secrets in production."""
    if not settings.debug:
        if settings.jwt_secret_key == "dev-secret-change-in-production":
            raise RuntimeError("JWT_SECRET_KEY must be set in production (not dev default)")
        if settings.encryption_key == "1tGkwxGdZgqzWY8sF0C--shdR3n8_PqAJkreObb--tU=":
            raise RuntimeError("ENCRYPTION_KEY must be set in production (not dev default)")
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"code": exc.code, "message": exc.message},
    )


@app.exception_handler(DuplicateError)
async def duplicate_error_handler(
    request: Request, exc: DuplicateError
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"code": exc.code, "message": exc.message},
    )


@app.exception_handler(BusinessError)
async def business_error_handler(
    request: Request, exc: BusinessError
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"code": exc.code, "message": exc.message},
    )


# Routers
app.include_router(root_router)
app.include_router(api_router)
