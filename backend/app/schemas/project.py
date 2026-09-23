"""Project request and response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.voice import VoiceProfileResponse


class AudioAssetResponse(BaseModel):
    """Audio asset metadata response."""

    id: str
    project_id: str | None = None
    filename: str
    file_path: str
    file_size: int
    duration: float | None = None
    sample_rate: int | None = None
    channels: int | None = None
    mime_type: str
    asset_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VideoAssetResponse(BaseModel):
    """Video asset metadata response."""

    id: str
    project_id: str | None = None
    filename: str
    file_path: str
    file_size: int
    duration: float | None = None
    resolution: str
    fps: int
    mime_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectBase(BaseModel):
    """Base fields for a poetry reel project."""

    title: str = Field(..., min_length=1, max_length=200, description="Title of the project")
    description: str | None = Field(None, max_length=2000)
    raw_poetry: str = Field(..., min_length=1, description="Raw Urdu poetry stanzas/couplets")
    voice_id: str | None = Field(None, description="Selected VoiceProfile UUID")
    bgm_path: str | None = Field(None, description="Path to background audio file")
    dsp_settings: dict[str, Any] | None = Field(
        default_factory=dict, description="Audio DSP mastering parameters"
    )
    subtitle_settings: dict[str, Any] | None = Field(
        default_factory=dict, description="Nastaliq typography styling settings"
    )


class ProjectCreate(ProjectBase):
    """Schema for creating a project."""

    pass


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    raw_poetry: str | None = None
    normalized_poetry: str | None = None
    voice_id: str | None = None
    bgm_path: str | None = None
    dsp_settings: dict[str, Any] | None = None
    subtitle_settings: dict[str, Any] | None = None
    status: str | None = None


class ProjectResponse(ProjectBase):
    """Schema returned for project queries."""

    id: str
    normalized_poetry: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    voice: VoiceProfileResponse | None = None
    audio_assets: list[AudioAssetResponse] = Field(default_factory=list)
    video_assets: list[VideoAssetResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
