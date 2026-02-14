from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router, root_router
from app.config import settings
from app.utils.errors import BusinessError, NotFoundError

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
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
