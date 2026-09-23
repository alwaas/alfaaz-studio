"""System status and diagnostics schemas."""

from typing import Any

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """System health response."""

    status: str = "healthy"
    app: str
    version: str
    environment: str
    device: str
    database_connected: bool = True


class ReadyResponse(BaseModel):
    """System readiness check response."""

    ready: bool
    checks: dict[str, bool]
    details: dict[str, Any] | None = None


class DeviceInfoResponse(BaseModel):
    """Compute device information and hardware status."""

    configured_device: str
    effective_device: str
    cuda_available: bool
    cuda_device_count: int = 0
    cuda_device_name: str | None = None
    cuda_vram_total_mb: float | None = None
    cuda_vram_used_mb: float | None = None
    cpu_cores_logical: int
    cpu_cores_physical: int | None = None
    cpu_usage_percent: float
    system_memory_total_mb: float
    system_memory_available_mb: float
    system_memory_used_percent: float


class ModelItem(BaseModel):
    """Information regarding a localized model weight."""

    name: str
    engine: str
    path: str
    installed: bool
    size_mb: float | None = None
    license_type: str


class ModelStatusResponse(BaseModel):
    """Model inventory and runtime engine status."""

    default_engine: str
    fallback_engine: str
    models_directory: str
    installed_count: int
    models: list[ModelItem]


class StorageLocationInfo(BaseModel):
    """Storage statistics for a specific directory."""

    path: str
    exists: bool
    total_bytes: int = 0
    used_bytes: int = 0
    free_bytes: int = 0
    percent_used: float = 0.0


class StorageStatusResponse(BaseModel):
    """Aggregated storage diagnostics for models, temp, and outputs."""

    models: StorageLocationInfo
    outputs: StorageLocationInfo
    temp: StorageLocationInfo
