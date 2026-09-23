"""Pydantic schemas for 9:16 vertical reel rendering endpoints."""

from pydantic import BaseModel, Field


class ReelThemePreset(BaseModel):
    """Visual aesthetic theme preset for poetry reels."""

    id: str
    name: str
    description: str
    bg_color_hex: str
    accent_color_hex: str


class ReelRenderRequest(BaseModel):
    """Request payload to render a 1080x1920 MP4 reel."""

    project_id: str
    audio_asset_id: str
    theme_id: str = "velvet-gold"
    bg_video_path: str | None = None
    font_name: str = "Noto Nastaliq Urdu"
    font_size: int = Field(default=60, ge=30, le=100)
    enable_karaoke: bool = True
    fps: int = Field(default=30, ge=15, le=60)


class ReelRenderResponse(BaseModel):
    """Response payload containing rendered video asset metadata."""

    video_asset_id: str
    project_id: str
    filename: str
    duration: float
    resolution: str
    fps: int
    stream_url: str
    download_url: str
    status: str = "rendered"
