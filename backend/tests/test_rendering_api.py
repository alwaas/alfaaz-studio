"""Integration tests for Reel Video Rendering API endpoints."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf  # type: ignore[import-untyped]
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AudioAsset, Project
from app.services.renderer import reel_renderer


@pytest.mark.asyncio
async def test_list_rendering_themes(client: AsyncClient) -> None:
    """Verifies listing available visual themes for reels."""
    res = await client.get("/api/v1/rendering/themes")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    theme_ids = [t["id"] for t in data]
    assert "velvet-gold" in theme_ids
    assert "emerald-night" in theme_ids
    assert "candlelight" in theme_ids
    assert "monochrome-rain" in theme_ids


@pytest.mark.asyncio
async def test_render_reel_endpoint(client: AsyncClient, db_session: AsyncSession) -> None:
    """Verifies end-to-end reel video rendering endpoint."""
    if not reel_renderer.is_ffmpeg_available():
        pytest.skip("FFmpeg not installed")

    # 1. Create project
    project = Project(
        title="شعر ریل",
        description="میر تقی میر",
        raw_poetry="اب کے جنوں میں فاصلہ شاید نہ کچھ رہے\nدامن کے چاک اور گریباں کے چاک میں",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # 2. Create audio file & asset
    sr = 24000
    duration = 1.0
    samples = (0.2 * np.sin(2.0 * np.pi * 330.0 * np.linspace(0, duration, int(duration * sr), endpoint=False))).astype(np.float32)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        sf.write(tmp_wav.name, samples, sr, subtype="PCM_16")
        wav_path = Path(tmp_wav.name)

    try:
        audio_asset = AudioAsset(
            project_id=project.id,
            filename=wav_path.name,
            file_path=str(wav_path),
            file_size=len(samples) * 2,
            duration=duration,
            sample_rate=sr,
            channels=1,
            mime_type="audio/wav",
            asset_type="mastered",
        )
        db_session.add(audio_asset)
        await db_session.commit()
        await db_session.refresh(audio_asset)

        # 3. Post render request
        payload = {
            "project_id": project.id,
            "audio_asset_id": audio_asset.id,
            "theme_id": "velvet-gold",
            "fps": 15,
            "font_size": 56,
        }

        res = await client.post("/api/v1/rendering/render", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "rendered"
        assert data["resolution"] == "1080x1920"
        assert "stream_url" in data
        assert "download_url" in data
        video_id = data["video_asset_id"]

        # 4. Test Stream endpoint
        stream_res = await client.get(f"/api/v1/rendering/videos/{video_id}/stream")
        assert stream_res.status_code == 200
        assert "video/mp4" in stream_res.headers["content-type"]
        assert len(stream_res.content) > 1000

        # 5. Test Download endpoint
        dl_res = await client.get(f"/api/v1/rendering/videos/{video_id}/download")
        assert dl_res.status_code == 200
        assert "attachment" in dl_res.headers.get("content-disposition", "")
    finally:
        wav_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_render_errors_and_404s(client: AsyncClient) -> None:
    """Verifies proper HTTP 404 responses for invalid rendering targets."""
    res_unknown_proj = await client.post(
        "/api/v1/rendering/render",
        json={"project_id": "non-existent-proj", "audio_asset_id": "non-existent-audio"},
    )
    assert res_unknown_proj.status_code == 404

    res_stream_404 = await client.get("/api/v1/rendering/videos/non-existent-video/stream")
    assert res_stream_404.status_code == 404

    res_dl_404 = await client.get("/api/v1/rendering/videos/non-existent-video/download")
    assert res_dl_404.status_code == 404
