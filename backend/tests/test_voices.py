"""Test voice profile CRUD endpoints."""

import pytest
from httpx import AsyncClient

from app.db.models import VoiceProfile


@pytest.mark.asyncio
async def test_create_voice_profile(client: AsyncClient) -> None:
    """Test creating a voice profile."""
    payload = {
        "name": "Allama Iqbal",
        "description": "Heroic, philosophical tone for national poetry",
        "gender": "male",
        "language": "ur",
        "engine": "f5-tts",
        "is_preset": False,
    }
    response = await client.post("/api/v1/voices", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Allama Iqbal"
    assert data["gender"] == "male"
    assert data["engine"] == "f5-tts"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_voice_profiles(client: AsyncClient, sample_voice: VoiceProfile) -> None:
    """Test listing voice profiles and filtering."""
    response = await client.get("/api/v1/voices")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(v["name"] == sample_voice.name for v in data)

    # Filter by gender
    filtered = await client.get("/api/v1/voices?gender=male")
    assert filtered.status_code == 200
    assert all(v["gender"] == "male" for v in filtered.json())

    # Filter with non-matching value
    empty = await client.get("/api/v1/voices?gender=unknown_gender")
    assert empty.status_code == 200
    assert len(empty.json()) == 0


@pytest.mark.asyncio
async def test_get_voice_profile_by_id(client: AsyncClient, sample_voice: VoiceProfile) -> None:
    """Test fetching a voice profile by ID."""
    response = await client.get(f"/api/v1/voices/{sample_voice.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_voice.id
    assert data["name"] == sample_voice.name


@pytest.mark.asyncio
async def test_get_voice_profile_not_found(client: AsyncClient) -> None:
    """Test 404 response for nonexistent voice profile ID."""
    response = await client.get("/api/v1/voices/nonexistent-id-0000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_voice_profile(client: AsyncClient, sample_voice: VoiceProfile) -> None:
    """Test deleting an existing voice profile."""
    del_res = await client.delete(f"/api/v1/voices/{sample_voice.id}")
    assert del_res.status_code == 204

    # Verify subsequent lookup returns 404
    get_res = await client.get(f"/api/v1/voices/{sample_voice.id}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_delete_voice_profile_not_found(client: AsyncClient) -> None:
    """Test 404 response when deleting a non-existent voice profile."""
    response = await client.delete("/api/v1/voices/nonexistent-id-0000")
    assert response.status_code == 404
