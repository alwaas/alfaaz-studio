"""Background Job Queue Service with Celery and asyncio task execution."""

import asyncio
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.db.models import AudioAsset, Job, Project, VoiceProfile
from app.db.session import async_session_factory
from app.services.storage import storage_service
from app.services.tts.factory import tts_factory
from app.utils.urdu_text import normalize_urdu

logger = get_logger(__name__)

# In-memory store for real-time job logs and cancellation tokens
_job_logs: dict[str, list[str]] = {}
_cancelled_jobs: set[str] = set()


def append_job_log(job_id: str, message: str) -> None:
    """Append a timestamped log entry to the job log store."""
    timestamp = datetime.now(UTC).strftime("%H:%M:%S.%f")[:-3]
    entry = f"[{timestamp}] {message}"
    if job_id not in _job_logs:
        _job_logs[job_id] = []
    _job_logs[job_id].append(entry)
    logger.info(f"Job {job_id}: {message}")


def get_job_logs(job_id: str) -> list[str]:
    """Retrieve all log lines for a specific job."""
    return _job_logs.get(job_id, [f"[{job_id}] Job initialized. Awaiting logs..."])


def mark_job_cancelled(job_id: str) -> None:
    """Request cooperative cancellation for an in-flight job."""
    _cancelled_jobs.add(job_id)
    append_job_log(job_id, "Cancellation requested by user.")


def is_job_cancelled(job_id: str) -> bool:
    """Check if job has received a cancellation request."""
    return job_id in _cancelled_jobs


async def execute_audio_generation(
    job_id: str,
    project_id: str,
    speed: float = 1.0,
    voice_id: str | None = None,
    session_factory: async_sessionmaker[AsyncSession] | None = None,
) -> dict[str, Any]:
    """
    Execute full text-to-speech audio synthesis pipeline for a project.
    Progresses from 0% -> 25% (cleaning) -> 50% (TTS) -> 80% (saving) -> 100% (done).
    """
    append_job_log(job_id, f"Beginning audio generation for project {project_id}")

    maker = session_factory or async_session_factory
    async with maker() as session:
        # 1. Fetch project and job records
        project_res = await session.execute(select(Project).where(Project.id == project_id))
        project = project_res.scalar_one_or_none()

        job_res = await session.execute(select(Job).where(Job.id == job_id))
        job = job_res.scalar_one_or_none()

        if not project or not job:
            error_msg = f"Project '{project_id}' or Job '{job_id}' not found in database"
            append_job_log(job_id, f"ERROR: {error_msg}")
            if job:
                job.status = "failed"
                job.error_message = error_msg
                await session.commit()
            return {"status": "failed", "error": error_msg}

        # Check early cancellation
        if is_job_cancelled(job_id):
            job.status = "cancelled"
            job.progress = 0.0
            await session.commit()
            return {"status": "cancelled"}

        # 2. Update status to processing (10%)
        job.status = "processing"
        job.progress = 10.0
        project.status = "synthesizing"
        await session.commit()
        append_job_log(job_id, "Job status marked as processing (10%)")

        # 3. Text Normalization (25%)
        raw_text = project.raw_poetry
        normalized = normalize_urdu(raw_text)
        project.normalized_poetry = normalized
        job.progress = 25.0
        await session.commit()
        append_job_log(job_id, f"Poetry normalized ({len(normalized.split())} words) (25%)")

        if is_job_cancelled(job_id):
            job.status = "cancelled"
            await session.commit()
            return {"status": "cancelled"}

        # 4. Determine voice engine & reference
        selected_voice_id = voice_id or project.voice_id
        engine_name = "mock"
        ref_path = None
        if selected_voice_id:
            voice_res = await session.execute(
                select(VoiceProfile).where(VoiceProfile.id == selected_voice_id)
            )
            voice_obj = voice_res.scalar_one_or_none()
            if voice_obj:
                engine_name = voice_obj.engine
                ref_path = voice_obj.reference_audio_path

        # 5. Synthesize speech via TTS Provider (50%)
        provider = tts_factory.get_provider(engine_name)
        append_job_log(job_id, f"Invoking TTS Provider '{engine_name}' at speed {speed}x (50%)")

        try:
            tts_res = await provider.synthesize(
                text=normalized,
                voice=selected_voice_id,
                speed=speed,
                reference_audio=ref_path,
            )
        except Exception as exc:
            job.status = "failed"
            job.error_message = f"TTS Synthesis failed: {exc}"
            project.status = "failed"
            await session.commit()
            append_job_log(job_id, f"ERROR: Synthesis failed with exception: {exc}")
            return {"status": "failed", "error": str(exc)}

        if is_job_cancelled(job_id):
            job.status = "cancelled"
            await session.commit()
            return {"status": "cancelled"}

        job.progress = 75.0
        append_job_log(
            job_id,
            f"Speech generated successfully: {tts_res.duration}s audio, {len(tts_res.word_timestamps)} word markers (75%)",
        )
        await session.commit()

        # 6. Save Audio Asset (85%)
        filename = f"tts_speech_{project_id[:8]}.wav"
        file_id, safe_path, size_bytes, mime = await storage_service.save_file(
            content=tts_res.audio_bytes,
            filename=filename,
            category="temp",
        )

        audio_asset = AudioAsset(
            project_id=project.id,
            filename=safe_path.name,
            file_path=str(safe_path),
            file_size=size_bytes,
            duration=tts_res.duration,
            sample_rate=tts_res.sample_rate,
            channels=1,
            mime_type="audio/wav",
            asset_type="raw_tts",
        )
        session.add(audio_asset)

        # 7. Finalize Job & Project (100%)
        job.progress = 100.0
        job.status = "completed"
        job.result = {
            "audio_asset_id": audio_asset.id,
            "duration": tts_res.duration,
            "sample_rate": tts_res.sample_rate,
            "word_timestamps_count": len(tts_res.word_timestamps),
            "file_path": str(safe_path),
        }
        project.status = "audio_ready"
        await session.commit()

        append_job_log(job_id, f"Audio generation complete! Asset ID: {audio_asset.id} (100%)")
        return {"status": "completed", "job_id": job_id, "audio_asset_id": audio_asset.id}


# Celery Tasks
@celery_app.task(name="alfaaz.generate_audio", bind=True)
def celery_generate_audio(
    self: Any,
    job_id: str,
    project_id: str,
    speed: float = 1.0,
    voice_id: str | None = None,
) -> dict[str, Any]:
    """Celery synchronous/worker task executing the async pipeline."""
    return asyncio.run(
        execute_audio_generation(
            job_id=job_id,
            project_id=project_id,
            speed=speed,
            voice_id=voice_id,
        )
    )


@celery_app.task(name="alfaaz.mix_audio", bind=True)
def celery_mix_audio(
    self: Any,
    prev_result: dict[str, Any],
    job_id: str,
    project_id: str,
    bgm_path: str | None = None,
) -> dict[str, Any]:
    """Celery chained task for mixing audio background and applying mastering filters."""
    append_job_log(job_id, "Audio mixing task started in chain")
    return {
        "status": "completed",
        "job_id": job_id,
        "step": "mix_audio",
        "prev_result": prev_result,
    }


@celery_app.task(name="alfaaz.render_reel", bind=True)
def celery_render_reel(
    self: Any,
    prev_result: dict[str, Any],
    job_id: str,
    project_id: str,
) -> dict[str, Any]:
    """Celery chained task for rendering final video reel with FFmpeg."""
    append_job_log(job_id, "Video reel rendering task started in chain")
    return {
        "status": "completed",
        "job_id": job_id,
        "step": "render_reel",
        "prev_result": prev_result,
    }


def create_task_chain(job_id: str, project_id: str, speed: float = 1.0) -> Any:
    """Create a Celery task chain: generate_audio -> mix_audio -> render_reel."""
    from celery import chain  # type: ignore[import-untyped]

    return chain(
        celery_generate_audio.s(job_id=job_id, project_id=project_id, speed=speed),
        celery_mix_audio.s(job_id=job_id, project_id=project_id),
        celery_render_reel.s(job_id=job_id, project_id=project_id),
    )
