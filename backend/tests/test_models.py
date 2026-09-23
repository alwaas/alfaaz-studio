"""Test database models and relationships."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import AudioAsset, Job, Project, VideoAsset, VoiceProfile


@pytest.mark.asyncio
async def test_models_lifecycle_and_relationships(db_session: AsyncSession) -> None:
    """Verify entity creation and relational cascades."""
    # 1. Create Voice Profile
    voice = VoiceProfile(
        name="Parveen Shakir Voice",
        description="Soft, evocative feminine recitation tone",
        gender="female",
        language="ur",
        engine="melotts",
        is_preset=True,
    )
    db_session.add(voice)
    await db_session.commit()
    await db_session.refresh(voice)
    assert voice.id is not None

    # 2. Create Project linked to Voice
    project = Project(
        title="Khushboo Ka Safar",
        raw_poetry="وہ تو خوشبو ہے ہواؤں میں بکھر جائے گا",
        voice_id=voice.id,
        status="draft",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # 3. Add Audio and Video Assets
    audio = AudioAsset(
        project_id=project.id,
        filename="recitation.wav",
        file_path="/mock/path/recitation.wav",
        file_size=10240,
        duration=15.5,
        sample_rate=24000,
        channels=1,
        mime_type="audio/wav",
        asset_type="raw_tts",
    )
    video = VideoAsset(
        project_id=project.id,
        filename="final_reel.mp4",
        file_path="/mock/path/final_reel.mp4",
        file_size=204800,
        duration=15.5,
        resolution="1080x1920",
        fps=30,
        mime_type="video/mp4",
    )
    job = Job(
        project_id=project.id,
        job_type="tts_synthesis",
        status="completed",
        progress=100.0,
    )
    db_session.add_all([audio, video, job])
    await db_session.commit()

    # 4. Verify loaded relationships
    q = (
        select(Project)
        .where(Project.id == project.id)
        .options(
            selectinload(Project.voice),
            selectinload(Project.audio_assets),
            selectinload(Project.video_assets),
            selectinload(Project.jobs),
        )
    )
    res = await db_session.execute(q)
    fetched_proj = res.scalar_one()

    assert fetched_proj.voice is not None
    assert fetched_proj.voice.name == "Parveen Shakir Voice"
    assert len(fetched_proj.audio_assets) == 1
    assert fetched_proj.audio_assets[0].filename == "recitation.wav"
    assert len(fetched_proj.video_assets) == 1
    assert fetched_proj.video_assets[0].filename == "final_reel.mp4"
    assert len(fetched_proj.jobs) == 1
    assert fetched_proj.jobs[0].job_type == "tts_synthesis"

    # 5. Verify cascade deletion
    await db_session.delete(fetched_proj)
    await db_session.commit()

    audio_res = await db_session.execute(
        select(AudioAsset).where(AudioAsset.project_id == project.id)
    )
    assert len(audio_res.scalars().all()) == 0
