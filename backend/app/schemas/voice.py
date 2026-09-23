"""Voice profile request and response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class VoiceProfileBase(BaseModel):
    """Base fields for a voice profile."""

    name: str = Field(..., min_length=1, max_length=100, description="Name of the voice profile")
    description: str | None = Field(None, max_length=1000)
    gender: str = Field("neutral", description="Voice gender: male, female, or neutral")
    language: str = Field("ur", description="Primary language code (e.g. ur)")
    engine: str = Field("f5-tts", description="Underlying synthesis engine (f5-tts, melotts, mock)")
    reference_audio_path: str | None = Field(None, description="Path to voice reference audio file")
    reference_text: str | None = Field(None, description="Transcript of the reference audio")
    is_preset: bool = Field(False, description="Whether this is a built-in studio preset")


class VoiceProfileCreate(VoiceProfileBase):
    """Schema for creating a new voice profile."""

    pass


class VoiceProfileUpdate(BaseModel):
    """Schema for updating an existing voice profile."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    gender: str | None = None
    language: str | None = None
    engine: str | None = None
    reference_audio_path: str | None = None
    reference_text: str | None = None
    is_preset: bool | None = None


class VoiceProfileResponse(VoiceProfileBase):
    """Schema returned for voice profile queries."""

    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
