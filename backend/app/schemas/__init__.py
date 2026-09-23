"""Schemas module initialization."""

from app.schemas.audio import (
    AudioMasteringRequest,
    AudioMasteringResponse,
    AudioTrimRequest,
    BGMPreset,
)
from app.schemas.job import (
    GenerateAudioRequest,
    JobLogsResponse,
    JobResponse,
)
from app.schemas.project import (
    AudioAssetResponse,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    VideoAssetResponse,
)
from app.schemas.rendering import (
    ReelRenderRequest,
    ReelRenderResponse,
    ReelThemePreset,
)
from app.schemas.system import (
    DeviceInfoResponse,
    HealthResponse,
    ModelItem,
    ModelStatusResponse,
    ReadyResponse,
    StorageLocationInfo,
    StorageStatusResponse,
)
from app.schemas.voice import (
    VoiceProfileCreate,
    VoiceProfileResponse,
    VoiceProfileUpdate,
)

__all__ = [
    "HealthResponse",
    "ReadyResponse",
    "DeviceInfoResponse",
    "ModelStatusResponse",
    "ModelItem",
    "StorageStatusResponse",
    "StorageLocationInfo",
    "VoiceProfileCreate",
    "VoiceProfileUpdate",
    "VoiceProfileResponse",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "AudioAssetResponse",
    "VideoAssetResponse",
    "GenerateAudioRequest",
    "JobResponse",
    "JobLogsResponse",
    "BGMPreset",
    "AudioMasteringRequest",
    "AudioTrimRequest",
    "AudioMasteringResponse",
    "ReelThemePreset",
    "ReelRenderRequest",
    "ReelRenderResponse",
]
