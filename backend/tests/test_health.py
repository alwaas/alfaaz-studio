"""Test health and readiness probes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient) -> None:
    """Verify health endpoint returns 200, healthy status, and app metadata."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert data["app"] == "AlfaazStudio"
    assert data["version"] == "0.1.0"
    assert "device" in data
    assert "database_connected" in data


@pytest.mark.asyncio
async def test_readiness_check_endpoint(client: AsyncClient) -> None:
    """Verify readiness probe returns operational checks."""
    response = await client.get("/api/v1/ready")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "ready" in data
    assert "checks" in data
    assert "database" in data["checks"]
    assert "temp_storage" in data["checks"]
