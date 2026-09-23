"""System diagnostics endpoints."""

from fastapi import APIRouter

from app.schemas.system import (
    DeviceInfoResponse,
    ModelStatusResponse,
    StorageStatusResponse,
)
from app.services.storage import storage_service
from app.services.system import system_service

router = APIRouter(prefix="/system", tags=["System Diagnostics"])


@router.get(
    "/device",
    response_model=DeviceInfoResponse,
    summary="Compute hardware diagnostics",
    description="Inspect CPU, memory, and CUDA GPU telemetry.",
)
async def get_device_status() -> DeviceInfoResponse:
    """Return compute device telemetry and hardware allocation status."""
    info = system_service.get_device_info()
    return DeviceInfoResponse(**info)


@router.get(
    "/model",
    response_model=ModelStatusResponse,
    summary="Model status and inventory",
    description="List downloaded local model weights and active synthesis engines.",
)
async def get_model_status() -> ModelStatusResponse:
    """Return local model weights inventory and engine readiness."""
    status = system_service.get_model_status()
    return ModelStatusResponse(**status)


@router.get(
    "/storage",
    response_model=StorageStatusResponse,
    summary="Storage diagnostics",
    description="Check disk capacity and usage for models, temp files, and rendered outputs.",
)
async def get_storage_status() -> StorageStatusResponse:
    """Return disk usage diagnostics for all media directories."""
    stats = storage_service.get_storage_stats()
    return StorageStatusResponse(
        models=stats["models"],  # type: ignore[arg-type]
        outputs=stats["outputs"],  # type: ignore[arg-type]
        temp=stats["temp"],  # type: ignore[arg-type]
    )
