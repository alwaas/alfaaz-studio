"""Unit tests for Audio Editor & DSP API endpoints."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf  # type: ignore[import-untyped]
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AudioAsset, Project


@pytest.mark.asyncio
async def test_list_bgm_presets(client: AsyncClient) -> None:
    """Verifies retrieval of curated background music presets."""
    response = await client.get("/api/v1/audio/bgm/presets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    preset_ids = [p["id"] for p in data]
    assert "rubab-meditative" in preset_ids
    assert "sitar-twilight" in preset_ids
    assert "flute-melancholy" in preset_ids
    assert "lofi-rain" in preset_ids


@pytest.mark.asyncio
async def test_stream_audio_asset(client: AsyncClient, db_session: AsyncSession) -> None:
    """Verifies audio streaming endpoint for Wavesurfer.js."""
    # 1. Create dummy project and audio file
    project = Project(
        title="Streaming Test",
        raw_poetry="شعر برائے ٹیسٹنگ",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Generate synthetic wav
    sr = 24000
    samples = (0.3 * np.sin(2.0 * np.pi * 440.0 * np.linspace(0, 1.0, sr, endpoint=False))).astype(
        np.float32
    )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, samples, sr, subtype="PCM_16")
        wav_path = Path(tmp.name)

    try:
        asset = AudioAsset(
            project_id=project.id,
            filename=wav_path.name,
            file_path=str(wav_path),
            file_size=len(samples) * 2,
            duration=1.0,
            sample_rate=sr,
            channels=1,
            mime_type="audio/wav",
            asset_type="raw_tts",
        )
        db_session.add(asset)
        await db_session.commit()
        await db_session.refresh(asset)

        # 2. Request streaming
        res = await client.get(f"/api/v1/audio/assets/{asset.id}/stream")
        assert res.status_code == 200
        assert "audio/wav" in res.headers["content-type"]
        assert len(res.content) > 1000
    finally:
        wav_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_master_audio_asset(client: AsyncClient, db_session: AsyncSession) -> None:
    """Verifies audio post-processing mastering endpoint."""
    project = Project(
        title="Mastering Project",
        raw_poetry="ستاروں سے آگے جہاں اور بھی ہیں",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    sr = 24000
    samples = (0.5 * np.sin(2.0 * np.pi * 220.0 * np.linspace(0, 1.5, int(1.5 * sr), endpoint=False))).astype(
        np.float32
    )

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, samples, sr, subtype="PCM_16")
        wav_path = Path(tmp.name)

    try:
        asset = AudioAsset(
            project_id=project.id,
            filename=wav_path.name,
            file_path=str(wav_path),
            file_size=len(samples) * 2,
            duration=1.5,
            sample_rate=sr,
            channels=1,
            mime_type="audio/wav",
            asset_type="raw_tts",
        )
        db_session.add(asset)
        await db_session.commit()
        await db_session.refresh(asset)

        # Request mastering with Warm EQ and BGM
        payload = {
            "asset_id": asset.id,
            "warmth_db": 3.0,
            "air_db": 2.0,
            "reverb_wet": 0.15,
            "room_size": 0.6,
            "enable_compression": True,
            "bgm_preset_id": "rubab-meditative",
            "bgm_volume": 0.2,
            "ducking_depth_db": -12.0,
        }

        res = await client.post("/api/v1/audio/master", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "mastered"
        assert data["duration"] > 1.0
        assert data["sample_rate"] == sr
        assert "stream_url" in data
    finally:
        wav_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_trim_silence_endpoint(client: AsyncClient, db_session: AsyncSession) -> None:
    """Verifies audio silence trimming endpoint."""
    project = Project(
        title="Trim Project",
        raw_poetry="خامشی میں بھی صدا ہے",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    sr = 24000
    silence = np.zeros(int(0.5 * sr), dtype=np.float32)
    voice = (0.6 * np.sin(2.0 * np.pi * 300.0 * np.linspace(0, 1.0, sr, endpoint=False))).astype(np.float32)
    audio = np.concatenate((silence, voice, silence))

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, audio, sr, subtype="PCM_16")
        wav_path = Path(tmp.name)

    try:
        asset = AudioAsset(
            project_id=project.id,
            filename=wav_path.name,
            file_path=str(wav_path),
            file_size=len(audio) * 2,
            duration=2.0,
            sample_rate=sr,
            channels=1,
            mime_type="audio/wav",
            asset_type="raw_tts",
        )
        db_session.add(asset)
        await db_session.commit()
        await db_session.refresh(asset)

        payload = {
            "asset_id": asset.id,
            "threshold_db": -35.0,
        }

        res = await client.post("/api/v1/audio/trim-silence", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "trimmed"
        assert data["duration"] < 2.0
    finally:
        wav_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_audio_asset_not_found(client: AsyncClient) -> None:
    """Verifies 404 response on unknown audio asset."""
    res = await client.get("/api/v1/audio/assets/non-existent-id/stream")
    assert res.status_code == 404

    res_master = await client.post("/api/v1/audio/master", json={"asset_id": "non-existent-id"})
    assert res_master.status_code == 404

    res_trim = await client.post("/api/v1/audio/trim-silence", json={"asset_id": "non-existent-id"})
    assert res_trim.status_code == 404

