"""SQLAlchemy database models for AlfaazStudio."""

import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utcnow() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(UTC)


class VoiceProfile(Base):
    """Voice profile representing a synthetic voice preset or cloned voice."""

    __tablename__ = "voice_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    gender: Mapped[str] = mapped_column(String(20), default="neutral")
    language: Mapped[str] = mapped_column(String(10), default="ur")
    engine: Mapped[str] = mapped_column(String(50), default="f5-tts")
    reference_audio_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reference_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # Relationships
    projects: Mapped[list["Project"]] = relationship(
        "Project", back_populates="voice", cascade="all, delete-orphan"
    )


class Project(Base):
    """Project entity representing a complete poetry reel creation."""

    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_poetry: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_poetry: Mapped[str | None] = mapped_column(Text, nullable=True)
    voice_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("voice_profiles.id", ondelete="SET NULL"), nullable=True
    )
    bgm_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    dsp_settings: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    subtitle_settings: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # Relationships
    voice: Mapped[Optional["VoiceProfile"]] = relationship(
        "VoiceProfile", back_populates="projects"
    )
    audio_assets: Mapped[list["AudioAsset"]] = relationship(
        "AudioAsset", back_populates="project", cascade="all, delete-orphan"
    )
    video_assets: Mapped[list["VideoAsset"]] = relationship(
        "VideoAsset", back_populates="project", cascade="all, delete-orphan"
    )
    jobs: Mapped[list["Job"]] = relationship(
        "Job", back_populates="project", cascade="all, delete-orphan"
    )


class AudioAsset(Base):
    """Audio asset belonging to a project or voice reference."""

    __tablename__ = "audio_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    sample_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    channels: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    asset_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # raw_tts, mastered, bgm, reference
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="audio_assets")


class VideoAsset(Base):
    """Rendered video reel asset for a project."""

    __tablename__ = "video_assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    resolution: Mapped[str] = mapped_column(String(50), default="1080x1920")
    fps: Mapped[int] = mapped_column(Integer, default=30)
    mime_type: Mapped[str] = mapped_column(String(100), default="video/mp4")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="video_assets")


class Job(Base):
    """Background asynchronous job execution state."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    project_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), default="queued", index=True
    )  # queued, processing, completed, failed, cancelled
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="jobs")
