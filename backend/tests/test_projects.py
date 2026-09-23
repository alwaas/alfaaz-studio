"""Test project CRUD endpoints."""

import pytest
from httpx import AsyncClient

from app.db.models import VoiceProfile


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient, sample_voice: VoiceProfile) -> None:
    """Test creating a project with valid data and voice reference."""
    payload = {
        "title": "Tere Khayal Ki Aaghosh",
        "description": "Romantic Urdu couplet reel",
        "raw_poetry": "دل سے جو بات نکلتی ہے اثر رکھتی ہے\nپر نہیں طاقت پرواز مگر رکھتی ہے",
        "voice_id": sample_voice.id,
        "dsp_settings": {"reverb_wet": 0.3, "warmth_db": 2.0},
        "subtitle_settings": {"font": "Jameel Noori Nastaleeq", "font_size": 42},
    }
    response = await client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Tere Khayal Ki Aaghosh"
    assert data["status"] == "draft"
    assert data["voice"]["id"] == sample_voice.id
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_project_invalid_voice(client: AsyncClient) -> None:
    """Test creating a project with nonexistent voice_id returns 400."""
    payload = {
        "title": "Invalid Voice Project",
        "raw_poetry": "کوئی امید بر نہیں آتی",
        "voice_id": "invalid-voice-id-1234",
    }
    response = await client.post("/api/v1/projects", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient) -> None:
    """Test listing projects with pagination and status filter."""
    # Create two projects
    await client.post(
        "/api/v1/projects",
        json={"title": "Project Alpha", "raw_poetry": "شعر ایک"},
    )
    await client.post(
        "/api/v1/projects",
        json={"title": "Project Beta", "raw_poetry": "شعر دو"},
    )

    response = await client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2

    # Status filter
    filtered = await client.get("/api/v1/projects?status=draft")
    assert filtered.status_code == 200
    assert len(filtered.json()) >= 2


@pytest.mark.asyncio
async def test_get_project_by_id(client: AsyncClient) -> None:
    """Test fetching a project by ID."""
    create_res = await client.post(
        "/api/v1/projects",
        json={"title": "Fetchable Project", "raw_poetry": "شعر ٹیسٹ"},
    )
    proj_id = create_res.json()["id"]

    get_res = await client.get(f"/api/v1/projects/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == proj_id
    assert get_res.json()["title"] == "Fetchable Project"


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient) -> None:
    """Test 404 response for nonexistent project ID."""
    response = await client.get("/api/v1/projects/nonexistent-project-0000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient) -> None:
    """Test deleting a project."""
    create_res = await client.post(
        "/api/v1/projects",
        json={"title": "Deletable Project", "raw_poetry": "شعر برائے حذف"},
    )
    proj_id = create_res.json()["id"]

    del_res = await client.delete(f"/api/v1/projects/{proj_id}")
    assert del_res.status_code == 204

    get_res = await client.get(f"/api/v1/projects/{proj_id}")
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_delete_project_not_found(client: AsyncClient) -> None:
    """Test deleting nonexistent project returns 404."""
    response = await client.delete("/api/v1/projects/nonexistent-project-0000")
    assert response.status_code == 404
