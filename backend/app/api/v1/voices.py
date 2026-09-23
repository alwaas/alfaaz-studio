"""Voice profile management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import VoiceProfile
from app.db.session import get_db
from app.schemas.voice import (
    VoiceProfileCreate,
    VoiceProfileResponse,
)

router = APIRouter(prefix="/voices", tags=["Voice Profiles"])


@router.post(
    "",
    response_model=VoiceProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create voice profile",
    description="Register a new voice profile preset or clone reference.",
)
async def create_voice_profile(
    payload: VoiceProfileCreate,
    db: AsyncSession = Depends(get_db),
) -> VoiceProfileResponse:
    """Create a new voice profile in the database."""
    voice = VoiceProfile(
        name=payload.name,
        description=payload.description,
        gender=payload.gender,
        language=payload.language,
        engine=payload.engine,
        reference_audio_path=payload.reference_audio_path,
        reference_text=payload.reference_text,
        is_preset=payload.is_preset,
    )
    db.add(voice)
    await db.commit()
    await db.refresh(voice)
    return VoiceProfileResponse.model_validate(voice)


@router.get(
    "",
    response_model=list[VoiceProfileResponse],
    summary="List voice profiles",
    description="Retrieve all registered voice profiles with optional filtering.",
)
async def list_voice_profiles(
    gender: str | None = Query(None, description="Filter by gender"),
    language: str | None = Query(None, description="Filter by language"),
    engine: str | None = Query(None, description="Filter by synthesis engine"),
    is_preset: bool | None = Query(None, description="Filter by preset status"),
    db: AsyncSession = Depends(get_db),
) -> list[VoiceProfileResponse]:
    """List all available voice profiles."""
    query = select(VoiceProfile)

    if gender is not None:
        query = query.where(VoiceProfile.gender == gender)
    if language is not None:
        query = query.where(VoiceProfile.language == language)
    if engine is not None:
        query = query.where(VoiceProfile.engine == engine)
    if is_preset is not None:
        query = query.where(VoiceProfile.is_preset == is_preset)

    query = query.order_by(VoiceProfile.name.asc())
    result = await db.execute(query)
    voices = result.scalars().all()
    return [VoiceProfileResponse.model_validate(v) for v in voices]


@router.get(
    "/{voice_id}",
    response_model=VoiceProfileResponse,
    summary="Get voice profile by ID",
    description="Fetch single voice profile metadata.",
)
async def get_voice_profile(
    voice_id: str,
    db: AsyncSession = Depends(get_db),
) -> VoiceProfileResponse:
    """Retrieve details of a specific voice profile."""
    query = select(VoiceProfile).where(VoiceProfile.id == voice_id)
    result = await db.execute(query)
    voice = result.scalar_one_or_none()

    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile with id '{voice_id}' not found",
        )

    return VoiceProfileResponse.model_validate(voice)


@router.delete(
    "/{voice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete voice profile",
    description="Delete a voice profile and its associated references.",
)
async def delete_voice_profile(
    voice_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Remove a voice profile from the database."""
    query = select(VoiceProfile).where(VoiceProfile.id == voice_id)
    result = await db.execute(query)
    voice = result.scalar_one_or_none()

    if not voice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Voice profile with id '{voice_id}' not found",
        )

    await db.delete(voice)
    await db.commit()
