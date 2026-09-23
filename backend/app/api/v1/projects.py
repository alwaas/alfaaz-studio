"""Project management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Project, VoiceProfile
from app.db.session import get_db
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
)

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create project",
    description="Initialize a new Urdu poetry reel project.",
)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Create a new project entity."""
    # Verify voice_id exists if provided
    if payload.voice_id:
        voice_res = await db.execute(
            select(VoiceProfile).where(VoiceProfile.id == payload.voice_id)
        )
        if not voice_res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Referenced voice profile '{payload.voice_id}' does not exist",
            )

    project = Project(
        title=payload.title,
        description=payload.description,
        raw_poetry=payload.raw_poetry,
        voice_id=payload.voice_id,
        bgm_path=payload.bgm_path,
        dsp_settings=payload.dsp_settings,
        subtitle_settings=payload.subtitle_settings,
        status="draft",
    )
    db.add(project)
    await db.commit()

    # Re-fetch with relationships loaded
    query = (
        select(Project)
        .where(Project.id == project.id)
        .options(
            selectinload(Project.voice),
            selectinload(Project.audio_assets),
            selectinload(Project.video_assets),
        )
    )
    result = await db.execute(query)
    saved_project = result.scalar_one()

    return ProjectResponse.model_validate(saved_project)


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="List projects",
    description="Retrieve all projects with optional status filtering.",
)
async def list_projects(
    status_filter: str | None = Query(None, alias="status", description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    """List projects in reverse chronological order."""
    query = (
        select(Project)
        .options(
            selectinload(Project.voice),
            selectinload(Project.audio_assets),
            selectinload(Project.video_assets),
        )
        .order_by(Project.created_at.desc())
        .offset(offset)
        .limit(limit)
    )

    if status_filter:
        query = query.where(Project.status == status_filter)

    result = await db.execute(query)
    projects = result.scalars().all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get project by ID",
    description="Fetch single project with voice and asset relationships.",
)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Retrieve full project details."""
    query = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.voice),
            selectinload(Project.audio_assets),
            selectinload(Project.video_assets),
        )
    )
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{project_id}' not found",
        )

    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete project",
    description="Delete project and cascade associated audio and video assets.",
)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a project entity."""
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id '{project_id}' not found",
        )

    await db.delete(project)
    await db.commit()
