"""FastAPI application entrypoint for AlfaazStudio."""

import time
import uuid
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.config import settings
from app.core.exceptions import (
    InvalidFileTypeException,
    ResourceNotFoundException,
    StorageSecurityException,
)
from app.core.logging import get_logger, request_id_ctx, setup_logging
from app.db.session import close_db, init_db

# Initialize structured logging
setup_logging(settings.LOG_LEVEL)
logger = get_logger("alfaaz.app")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager for startup and shutdown hooks."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.APP_ENV})")
    # Initialize database schemas
    await init_db()
    logger.info("Database schemas verified and initialized")
    yield
    # Graceful shutdown
    logger.info("Shutting down database connection pool...")
    await close_db()
    logger.info("Shutdown complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Urdu Poetry AI Voice-over Studio for Instagram Reels",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_id_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware attaching a unique correlation ID to requests and logs."""
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    token = request_id_ctx.set(req_id)
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response
    finally:
        request_id_ctx.reset(token)


@app.exception_handler(StorageSecurityException)
async def storage_security_handler(request: Request, exc: StorageSecurityException) -> JSONResponse:
    logger.warning(f"Storage security violation: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "StorageSecurityError", "message": exc.message},
    )


@app.exception_handler(InvalidFileTypeException)
async def invalid_file_type_handler(
    request: Request, exc: InvalidFileTypeException
) -> JSONResponse:
    logger.warning(f"Invalid file type: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        content={"error": "InvalidFileTypeError", "message": exc.message},
    )


@app.exception_handler(ResourceNotFoundException)
async def not_found_handler(request: Request, exc: ResourceNotFoundException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "NotFoundError", "message": exc.message},
    )


# Mount API v1 router
app.include_router(api_v1_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
