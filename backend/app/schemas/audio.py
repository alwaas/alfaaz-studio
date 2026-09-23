"""Pydantic schemas for audio mastering and editor endpoints."""

from pydantic import BaseModel, Field


class BGMPreset(BaseModel):
    """Background music track preset definition."""

    id: str
    name: str
    category: str
    description: str


class AudioMasteringRequest(BaseModel):
    """Request payload to apply DSP mastering to an audio asset."""

    asset_id: str
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: float = Field(default=0.0, ge=-1.0, le=1.0)
    warmth_db: float = Field(default=2.5, ge=0.0, le=8.0)
    air_db: float = Field(default=1.5, ge=0.0, le=6.0)
    reverb_wet: float = Field(default=0.15, ge=0.0, le=0.5)
    room_size: float = Field(default=0.5, ge=0.1, le=1.0)
    enable_compression: bool = True
    compressor_threshold_db: float = Field(default=-16.0, ge=-40.0, le=0.0)
    bgm_preset_id: str | None = None
    bgm_volume: float = Field(default=0.25, ge=0.0, le=1.0)
    ducking_depth_db: float = Field(default=-14.0, ge=-30.0, le=-3.0)


class AudioTrimRequest(BaseModel):
    """Request payload to trim silence from an audio asset."""

    asset_id: str
    threshold_db: float = Field(default=-40.0, ge=-60.0, le=-10.0)


class AudioMasteringResponse(BaseModel):
    """Response payload containing mastered audio asset details."""

    asset_id: str
    project_id: str | None = None
    filename: str
    duration: float
    sample_rate: int
    stream_url: str
    status: str = "mastered"

