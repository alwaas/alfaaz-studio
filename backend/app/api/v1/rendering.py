"""Reel Video Rendering API Endpoints."""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AudioAsset, Project, VideoAsset
from app.db.session import get_db
from app.schemas.rendering import (
    ReelRenderRequest,
    ReelRenderResponse,
    ReelThemePreset,
)
from app.services.renderer import REEL_THEMES, reel_renderer
from app.services.storage import storage_service
from app.services.subtitles import SubtitleVerse
from app.utils.urdu_text import UrduTextNormalizer

router = APIRouter(prefix="/rendering", tags=["Reel Video Rendering"])


@router.get("/themes", response_model=list[ReelThemePreset])
async def list_reel_themes() -> list[ReelThemePreset]:
    """Returns curated visual aesthetic themes for 9:16 vertical reels."""
    return [
        ReelThemePreset(
            id=t.id,
            name=t.name,
            description=t.description,
            bg_color_hex=t.bg_color_hex,
            accent_color_hex=t.accent_color_hex,
        )
        for t in REEL_THEMES.values()
    ]


@router.post("/render", response_model=ReelRenderResponse)
async def render_video_reel(
    payload: ReelRenderRequest,
    db: AsyncSession = Depends(get_db),
) -> ReelRenderResponse:
    """Renders a cinematic 1080x1920 MP4 reel combining audio, canvas, and subtitles."""
    # 1. Fetch Project
    proj_query = select(Project).where(Project.id == payload.project_id)
    proj_res = await db.execute(proj_query)
    project = proj_res.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{payload.project_id}' not found.",
        )

    # 2. Fetch AudioAsset
    audio_query = select(AudioAsset).where(AudioAsset.id == payload.audio_asset_id)
    audio_res = await db.execute(audio_query)
    audio_asset = audio_res.scalar_one_or_none()
    if not audio_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio asset with ID '{payload.audio_asset_id}' not found.",
        )

    audio_path = Path(audio_asset.file_path)
    if not audio_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file '{audio_asset.filename}' does not exist on disk.",
        )

    total_duration = float(audio_asset.duration or 5.0)

    # 3. Parse Poetry into SubtitleVerses
    verses_raw = UrduTextNormalizer.split_verses(project.raw_poetry)
    if not verses_raw:
        verses_raw = [project.raw_poetry]

    num_verses = len(verses_raw)
    verse_duration = total_duration / float(max(1, num_verses))

    subtitle_verses: list[SubtitleVerse] = []
    for idx, verse_text in enumerate(verses_raw):
        v_start = round(idx * verse_duration, 2)
        v_end = round(min(total_duration, (idx + 1) * verse_duration), 2)
        subtitle_verses.append(
            SubtitleVerse(
                text=verse_text,
                start_time=v_start,
                end_time=v_end,
            )
        )

    # 4. Prepare output destination
    pid_str = str(project.id)[:8]
    aid_str = str(audio_asset.id)[:6]
    output_filename = f"reel_{pid_str}_{aid_str}.mp4"
    temp_dir = Path("temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_render_path = temp_dir / output_filename

    # Optional background video path
    bg_video: Path | None = None
    if payload.bg_video_path:
        bg_video = Path(payload.bg_video_path)

    # 5. Execute render
    try:
        rendered_path = await reel_renderer.render_reel(
            audio_path=audio_path,
            verses=subtitle_verses,
            output_path=temp_render_path,
            duration=total_duration,
            title=project.title,
            poet_name=project.description,
            bg_video_path=bg_video,
            theme_id=payload.theme_id,
            font_name=payload.font_name,
            font_size=payload.font_size,
            enable_karaoke=payload.enable_karaoke,
            fps=payload.fps,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video rendering failed: {exc}",
        ) from exc

    # 6. Save rendered MP4 to permanent storage
    video_bytes = rendered_path.read_bytes()
    file_id, safe_path, size_bytes, _ = await storage_service.save_file(
        content=video_bytes,
        filename=output_filename,
        category="outputs",
    )

    # Clean up temp render
    rendered_path.unlink(missing_ok=True)

    # 7. Record VideoAsset in DB
    video_asset = VideoAsset(
        project_id=project.id,
        filename=safe_path.name,
        file_path=str(safe_path),
        file_size=size_bytes,
        duration=total_duration,
        resolution="1080x1920",
        fps=payload.fps,
        mime_type="video/mp4",
    )
    db.add(video_asset)
    await db.commit()
    await db.refresh(video_asset)

    return ReelRenderResponse(
        video_asset_id=str(video_asset.id),
        project_id=str(project.id),
        filename=str(video_asset.filename),
        duration=float(total_duration),
        resolution=str(video_asset.resolution),
        fps=int(video_asset.fps),
        stream_url=f"/api/v1/rendering/videos/{video_asset.id}/stream",
        download_url=f"/api/v1/rendering/videos/{video_asset.id}/download",
        status="rendered",
    )


@router.get("/videos/{video_id}/stream")
async def stream_video_reel(
    video_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Streams the rendered MP4 reel with byte-range header support."""
    query = select(VideoAsset).where(VideoAsset.id == video_id)
    res = await db.execute(query)
    asset = res.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video asset with ID '{video_id}' not found.",
        )

    file_path = Path(asset.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video file '{asset.filename}' does not exist on disk.",
        )

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=asset.filename,
    )


@router.get("/videos/{video_id}/download")
async def download_video_reel(
    video_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Downloads the rendered MP4 reel as an attachment."""
    query = select(VideoAsset).where(VideoAsset.id == video_id)
    res = await db.execute(query)
    asset = res.scalar_one_or_none()

    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video asset with ID '{video_id}' not found.",
        )

    file_path = Path(asset.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video file '{asset.filename}' does not exist on disk.",
        )

    return FileResponse(
        path=str(file_path),
        media_type="video/mp4",
        filename=asset.filename,
        headers={"Content-Disposition": f'attachment; filename="{asset.filename}"'},
    )
