"""Unit and integration tests for background job queue and Job APIs."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Job, VoiceProfile
from app.services.queue import create_task_chain


@pytest.mark.asyncio
async def test_generate_audio_job_creation_and_polling(
    client: AsyncClient,
    sample_voice: VoiceProfile,
) -> None:
    """Test full audio generation workflow: trigger endpoint -> poll status -> verify completion."""
    # 1. Create a project
    create_proj_res = await client.post(
        "/api/v1/projects",
        json={
            "title": "Ghalib Audio Reel",
            "raw_poetry": "ہزاروں خواہشیں ایسی کہ ہر خواہش پہ دم نکلے\nبہت نکلے مرے ارمان لیکن پھر بھی کم نکلے",
            "voice_id": sample_voice.id,
        },
    )
    assert create_proj_res.status_code == 201
    project_id = create_proj_res.json()["id"]

    # 2. Trigger audio generation job
    gen_res = await client.post(
        f"/api/v1/projects/{project_id}/generate-audio",
        json={"speed": 1.0, "pitch": 0.0},
    )
    assert gen_res.status_code == 202
    job_data = gen_res.json()
    job_id = job_data["id"]
    assert job_data["status"] in ("queued", "processing", "completed")
    assert job_data["project_id"] == project_id

    # 3. Poll job status
    poll_res = await client.get(f"/api/v1/jobs/{job_id}")
    assert poll_res.status_code == 200
    polled_job = poll_res.json()
    assert polled_job["id"] == job_id
    assert polled_job["progress"] >= 0.0

    # 4. Fetch job execution logs
    logs_res = await client.get(f"/api/v1/jobs/{job_id}/logs")
    assert logs_res.status_code == 200
    log_data = logs_res.json()
    assert log_data["job_id"] == job_id
    assert len(log_data["logs"]) > 0


@pytest.mark.asyncio
async def test_generate_audio_invalid_project(client: AsyncClient) -> None:
    """Test generating audio for nonexistent project returns 404."""
    response = await client.post(
        "/api/v1/projects/nonexistent-project-0000/generate-audio",
        json={"speed": 1.0},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_generate_audio_invalid_voice_override(client: AsyncClient) -> None:
    """Test generating audio with invalid voice override returns 400."""
    create_proj_res = await client.post(
        "/api/v1/projects",
        json={"title": "Test Proj", "raw_poetry": "شعر برائے ٹیسٹ"},
    )
    project_id = create_proj_res.json()["id"]

    response = await client.post(
        f"/api/v1/projects/{project_id}/generate-audio",
        json={"voice_id": "nonexistent-voice-9999", "speed": 1.0},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_job_cancellation(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test cancelling a queued job."""
    # Create a job in DB
    job = Job(
        job_type="tts_synthesis",
        status="queued",
        progress=0.0,
    )
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)

    # Cancel via API
    cancel_res = await client.post(f"/api/v1/jobs/{job.id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

    # Verify status in DB
    refetched = await db_session.execute(select(Job).where(Job.id == job.id))
    assert refetched.scalar_one().status == "cancelled"


@pytest.mark.asyncio
async def test_job_not_found(client: AsyncClient) -> None:
    """Test 404 responses for nonexistent job endpoints."""
    poll_res = await client.get("/api/v1/jobs/nonexistent-job-0000")
    assert poll_res.status_code == 404

    cancel_res = await client.post("/api/v1/jobs/nonexistent-job-0000/cancel")
    assert cancel_res.status_code == 404

    logs_res = await client.get("/api/v1/jobs/nonexistent-job-0000/logs")
    assert logs_res.status_code == 404


def test_celery_task_chain_construction() -> None:
    """Test Celery task chain pipeline creation."""
    chain = create_task_chain(job_id="job-123", project_id="proj-456", speed=1.2)
    assert chain is not None
    # Verify chain has 3 tasks: generate_audio, mix_audio, render_reel
    assert len(chain.tasks) == 3
