"""Test system telemetry and diagnostic endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_system_device_endpoint(client: AsyncClient) -> None:
    """Verify compute device endpoint returns valid telemetry."""
    response = await client.get("/api/v1/system/device")
    assert response.status_code == 200
    data = response.json()
    assert "configured_device" in data
    assert "effective_device" in data
    assert "cuda_available" in data
    assert "cpu_cores_logical" in data
    assert data["cpu_cores_logical"] >= 1
    assert "system_memory_total_mb" in data
    assert data["system_memory_total_mb"] > 0


@pytest.mark.asyncio
async def test_system_model_endpoint(client: AsyncClient) -> None:
    """Verify system model status returns engine inventory."""
    response = await client.get("/api/v1/system/model")
    assert response.status_code == 200
    data = response.json()
    assert data["default_engine"] == "f5-tts"
    assert "models_directory" in data
    assert "installed_count" in data
    assert isinstance(data["models"], list)
    assert len(data["models"]) >= 4

    engines = [m["engine"] for m in data["models"]]
    assert "f5-tts" in engines
    assert "melotts" in engines
    assert "piper" in engines
    assert "whisper" in engines


@pytest.mark.asyncio
async def test_system_storage_endpoint(client: AsyncClient) -> None:
    """Verify storage diagnostics endpoint returns models, outputs, and temp stats."""
    response = await client.get("/api/v1/system/storage")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "outputs" in data
    assert "temp" in data
    assert "exists" in data["models"]
    assert "total_bytes" in data["models"]
