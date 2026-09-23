"""Initial schema creation

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-23 12:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. voice_profiles
    op.create_table(
        "voice_profiles",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("gender", sa.String(length=20), server_default="neutral", nullable=False),
        sa.Column("language", sa.String(length=10), server_default="ur", nullable=False),
        sa.Column("engine", sa.String(length=50), server_default="f5-tts", nullable=False),
        sa.Column("reference_audio_path", sa.String(length=500), nullable=True),
        sa.Column("reference_text", sa.Text(), nullable=True),
        sa.Column("is_preset", sa.Boolean(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_voice_profiles_name", "voice_profiles", ["name"])

    # 2. projects
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("raw_poetry", sa.Text(), nullable=False),
        sa.Column("normalized_poetry", sa.Text(), nullable=True),
        sa.Column("voice_id", sa.String(length=36), sa.ForeignKey("voice_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("bgm_path", sa.String(length=500), nullable=True),
        sa.Column("dsp_settings", sa.JSON(), nullable=True),
        sa.Column("subtitle_settings", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="draft", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_projects_title", "projects", ["title"])
    op.create_index("ix_projects_status", "projects", ["status"])

    # 3. audio_assets
    op.create_table(
        "audio_assets",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("sample_rate", sa.Integer(), nullable=True),
        sa.Column("channels", sa.Integer(), nullable=True),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_audio_assets_project_id", "audio_assets", ["project_id"])

    # 4. video_assets
    op.create_table(
        "video_assets",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("duration", sa.Float(), nullable=True),
        sa.Column("resolution", sa.String(length=50), server_default="1080x1920", nullable=False),
        sa.Column("fps", sa.Integer(), server_default="30", nullable=False),
        sa.Column("mime_type", sa.String(length=100), server_default="video/mp4", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_video_assets_project_id", "video_assets", ["project_id"])

    # 5. jobs
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("job_type", sa.String(length=50), nullable=False),
        sa.Column("project_id", sa.String(length=36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=True),
        sa.Column("status", sa.String(length=50), server_default="queued", nullable=False),
        sa.Column("progress", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("result", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_jobs_job_type", "jobs", ["job_type"])
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_project_id", "jobs", ["project_id"])


def downgrade() -> None:
    op.drop_table("jobs")
    op.drop_table("video_assets")
    op.drop_table("audio_assets")
    op.drop_table("projects")
    op.drop_table("voice_profiles")
