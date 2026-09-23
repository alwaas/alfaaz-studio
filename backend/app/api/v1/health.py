"""Health and readiness endpoints."""

from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.config import settings
from app.db.session import engine
from app.schemas.system import HealthResponse, ReadyResponse
from app.services.system import system_service

router = APIRouter(tags=["Health & Readiness"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check probe",
    description="Check core process health and database availability.",
)
async def health_check() -> HealthResponse:
    """Return fundamental system health status."""
    db_connected = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        db_connected = False

    return HealthResponse(
        status="healthy" if db_connected else "degraded",
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        device=settings.DEVICE,
        database_connected=db_connected,
    )


@router.get(
    "/ready",
    response_model=ReadyResponse,
    summary="Readiness check probe",
    description="Verify database connectivity and storage volume read/write accessibility.",
)
async def readiness_check(response: Response) -> ReadyResponse:
    """Readiness probe for load balancers and container orchestrators."""
    result = await system_service.check_readiness()
    if not result["ready"]:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadyResponse(
        ready=result["ready"],
        checks=result["checks"],
        details=result["details"],
    )
