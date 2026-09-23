"""Job and audio generation request and response schemas."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class GenerateAudioRequest(BaseModel):
    """Payload for initiating text-to-speech audio synthesis on a project."""
    voice_id: Optional[str] = Field(None, description="Optional override for project's selected VoiceProfile")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="Recitation speed multiplier (0.5x - 2.0x)")
    pitch: float = Field(0.0, ge=-1.0, le=1.0, description="Pitch adjustment")


class JobResponse(BaseModel):
    """Diagnostic response representing asynchronous job progress and state."""
    id: str
    job_type: str
    project_id: Optional[str] = None
    status: str
    progress: float
    error_message: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
    result: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobLogsResponse(BaseModel):
    """Job log output and state progression."""
    job_id: str
    status: str
    logs: list[str]

