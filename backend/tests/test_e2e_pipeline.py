"""End-to-End Automated Integration Test for AlfaazStudio Pipeline.

Validates the full lifecycle:
Project Creation -> Voice Selection -> TTS Synthesis -> Audio DSP Mastering
-> ASS Subtitle Generation -> FFmpeg 9:16 Video Rendering -> Output Validation.
"""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf  # type: ignore[import-untyped]
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AudioAsset, Project, VideoAsset, VoiceProfile
from app.services.dsp import audio_dsp
from app.services.renderer import REEL_THEMES, reel_renderer
from app.services.storage import storage_service
from app.services.subtitles import ASSSubtitleBuilder, SubtitleVerse
from app.services.tts.mock_provider import MockTTSProvider
from app.utils.urdu_text import UrduTextNormalizer


@pytest.mark.asyncio
async def test_full_e2e_studio_pipeline(client: AsyncClient, db_session: AsyncSession) -> None:
    """Verifies complete end-to-end studio flow from raw Urdu text to 9:16 MP4 reel."""
    # Step 1: Create Voice Profile
    voice = VoiceProfile(
        name="شاعرانہ آواز (Mirza Voice)",
        engine="mock",
        language="ur",
        gender="male",
        is_preset=True,
    )
    db_session.add(voice)
    await db_session.commit()
    await db_session.refresh(voice)
    assert voice.id is not None

    # Step 2: Create Poetry Project
    poetry_text = "دل ناداں تجھے ہوا کیا ہے\nآخر اس درد کی دوا کیا ہے"
    project = Project(
        title="دل ناداں - مرزا غالب",
        description="مرزا اسد اللہ خان غالب",
        raw_poetry=poetry_text,
        normalized_poetry=UrduTextNormalizer.clean_text(poetry_text),
        voice_id=voice.id,
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)
    assert project.id is not None

    # Step 3: Audio Synthesis (using mock provider)
    import io
    tts_provider = MockTTSProvider()
    tts_result = await tts_provider.synthesize(
        text=project.raw_poetry,
        speed=1.0,
    )
    audio_data, sr = sf.read(io.BytesIO(tts_result.audio_bytes), dtype="float32")
    assert sr == 24000
    assert len(audio_data) > 0
    assert len(tts_result.word_timestamps) > 0

    # Step 4: DSP Mastering (Warm EQ, Schroeder Reverb, Dynamic Compressor, BGM Ducking)
    from app.services.dsp import AudioDSPParams

    dsp_params = AudioDSPParams(
        eq_warmth_db=3.0,
        eq_air_db=2.0,
        reverb_wet=0.15,
        reverb_room_size=0.5,
        enable_compression=True,
        compressor_threshold_db=-16.0,
    )
    mastered_audio = audio_dsp.mix_and_master(
        voice_audio=audio_data,
        bgm_audio=None,
        sample_rate=sr,
        bgm_volume=0.2,
        ducking_depth_db=-14.0,
        dsp_params=dsp_params,
    )
    assert len(mastered_audio) > 0

    # Save Mastered Audio to Storage
    mastered_wav_bytes = audio_dsp.audio_to_wav_bytes(mastered_audio, sr)
    _, audio_path, audio_size, _ = await storage_service.save_file(
        content=mastered_wav_bytes,
        filename=f"mastered_e2e_{project.id[:8]}.wav",
        category="outputs",
    )

    audio_duration = round(len(mastered_audio) / float(sr), 3)
    audio_asset = AudioAsset(
        project_id=project.id,
        filename=audio_path.name,
        file_path=str(audio_path),
        file_size=audio_size,
        duration=audio_duration,
        sample_rate=sr,
        channels=1,
        mime_type="audio/wav",
        asset_type="mastered",
    )
    db_session.add(audio_asset)
    await db_session.commit()
    await db_session.refresh(audio_asset)

    # Step 5: ASS Subtitle Generation
    from app.services.tts.provider import WordTimestamp

    parsed_words = [
        WordTimestamp(
            word=w["word"],
            start_time=w["start_time"],
            end_time=w["end_time"],
        )
        for w in tts_result.word_timestamps
    ]

    verses = UrduTextNormalizer.split_verses(project.raw_poetry)
    verse_dur = audio_duration / float(len(verses))
    subtitle_verses = [
        SubtitleVerse(
            text=verse_text,
            start_time=round(i * verse_dur, 2),
            end_time=round((i + 1) * verse_dur, 2),
            words=parsed_words,
        )
        for i, verse_text in enumerate(verses)
    ]

    sub_builder = ASSSubtitleBuilder(
        font_name="Noto Nastaliq Urdu",
        font_size=58,
        resolution_x=1080,
        resolution_y=1920,
    )
    ass_content = sub_builder.build_ass_content(
        verses=subtitle_verses,
        title=project.title,
        poet_name=project.description,
        enable_karaoke=True,
    )
    assert "[Script Info]" in ass_content
    assert "PlayResX: 1080" in ass_content
    assert "PlayResY: 1920" in ass_content
    assert "Nastaliq_Main" in ass_content

    # Step 6: FFmpeg 9:16 Video Rendering (if FFmpeg present)
    if reel_renderer.is_ffmpeg_available():
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_out:
            e2e_video_temp = Path(tmp_out.name)

        try:
            rendered_video = await reel_renderer.render_reel(
                audio_path=Path(audio_asset.file_path),
                verses=subtitle_verses,
                output_path=e2e_video_temp,
                duration=audio_duration,
                title=project.title,
                poet_name=project.description,
                theme_id="velvet-gold",
                fps=15,  # Accelerated fps for integration test
            )

            assert rendered_video.exists()
            assert rendered_video.stat().st_size > 2000

            # Step 7: Record Video Asset
            video_bytes = rendered_video.read_bytes()
            _, safe_vid_path, vid_size, _ = await storage_service.save_file(
                content=video_bytes,
                filename=f"reel_e2e_{project.id[:8]}.mp4",
                category="outputs",
            )

            video_asset = VideoAsset(
                project_id=project.id,
                filename=safe_vid_path.name,
                file_path=str(safe_vid_path),
                file_size=vid_size,
                duration=audio_duration,
                resolution="1080x1920",
                fps=15,
                mime_type="video/mp4",
            )
            db_session.add(video_asset)
            await db_session.commit()
            await db_session.refresh(video_asset)

            # Step 8: Verify Complete Project Hierarchy via API
            proj_resp = await client.get(f"/api/v1/projects/{project.id}")
            assert proj_resp.status_code == 200
            proj_data = proj_resp.json()
            assert proj_data["id"] == project.id
            assert len(proj_data["audio_assets"]) >= 1
            assert len(proj_data["video_assets"]) >= 1

            # Verify Stream endpoints
            audio_stream_res = await client.get(f"/api/v1/audio/assets/{audio_asset.id}/stream")
            assert audio_stream_res.status_code == 200

            video_stream_res = await client.get(f"/api/v1/rendering/videos/{video_asset.id}/stream")
            assert video_stream_res.status_code == 200
        finally:
            e2e_video_temp.unlink(missing_ok=True)
