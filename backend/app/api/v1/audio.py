"""Audio editor and mastering endpoints."""

from pathlib import Path

import numpy as np
import scipy.signal  # type: ignore[import-untyped]
import soundfile as sf  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AudioAsset
from app.db.session import get_db
from app.schemas.audio import (
  AudioMasteringRequest,
  AudioMasteringResponse,
  AudioTrimRequest,
  BGMPreset,
)
from app.services.dsp import AudioDSPParams, audio_dsp
from app.services.storage import storage_service
from app.services.tts.voice_cloning import voice_preprocessor

router = APIRouter(prefix="/audio", tags=["Audio Editor & DSP"])

CURATED_BGM_PRESETS: list[BGMPreset] = [
  BGMPreset(
      id="rubab-meditative",
      name="Rubab Meditative (رباب)",
      category="traditional",
      description=(
          "Soulful and slow acoustic Rubab strums, capturing traditional"
          " Ghazal intimacy."
      ),
  ),
  BGMPreset(
      id="sitar-twilight",
      name="Sitar Twilight (ستار)",
      category="classical",
      description=(
          "Classical Raag Bhairavi Sitar resonance, evocative and romantic."
      ),
  ),
  BGMPreset(
      id="flute-melancholy",
      name="Bansuri Drone (بانسری)",
      category="ambient",
      description=(
          "Contemplative wooden flute drone, ideal for melancholic"
          " couplets."
      ),
  ),
  BGMPreset(
      id="lofi-rain",
      name="Lo-Fi Rain & Vinyl (بارش اور لو فائی)",
      category="modern",
      description=(
          "Soft rain ambience with vintage vinyl crackle, modern viral Reel"
          " aesthetic."
      ),
  ),
]


def generate_synthetic_bgm(
    preset_id: str, duration: float, sample_rate: int
) -> np.ndarray:
  """Generates a pleasant ambient synthetic accompaniment matching the preset."""
  num_samples = int(duration * sample_rate)
  t = np.linspace(0, duration, num_samples, endpoint=False)

  match preset_id:
    case "rubab-meditative":
      # Plucked harmonic chords around D minor (146.8 Hz, 220 Hz, 293.7 Hz)
      drone = 0.15 * np.sin(2.0 * np.pi * 146.8 * t) + 0.10 * np.sin(
          2.0 * np.pi * 220.0 * t
      )
      mod = 1.0 + 0.2 * np.sin(2.0 * np.pi * 0.5 * t)
      bgm = drone * mod
    case "sitar-twilight":
      # Rich harmonic sitar drone with gentle vibrato
      f0 = 130.8
      bgm = (
          0.18 * np.sin(2.0 * np.pi * f0 * t)
          + 0.12 * np.sin(2.0 * np.pi * (2.0 * f0) * t)
          + 0.08 * np.sin(2.0 * np.pi * (3.0 * f0) * t)
      )
      bgm *= 1.0 + 0.15 * np.sin(2.0 * np.pi * 4.0 * t)
    case "flute-melancholy":
      # Gentle breathy flute melody (F#4 370 Hz)
      flute = 0.20 * np.sin(2.0 * np.pi * 370.0 * t) + 0.05 * np.sin(
          2.0 * np.pi * 740.0 * t
      )
      env = 1.0 + 0.1 * np.sin(2.0 * np.pi * 0.25 * t)
      bgm = flute * env
    case "lofi-rain":
      # Filtered gentle white noise simulating rainfall
      noise = np.random.normal(0, 0.05, num_samples)
      b, a = scipy.signal.butter(2, 1200.0 / (sample_rate / 2), btype="low")
      bgm = scipy.signal.lfilter(b, a, noise)
    case _:
      bgm = 0.1 * np.sin(2.0 * np.pi * 220.0 * t)

  return bgm.astype(np.float32)


@router.get("/bgm/presets", response_model=list[BGMPreset])
async def list_bgm_presets() -> list[BGMPreset]:
  """Returns the catalog of curated background music and acoustic ambience presets."""
  return CURATED_BGM_PRESETS


@router.get("/assets/{asset_id}/stream")
async def stream_audio_asset(
    asset_id: str,
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
  """Streams or downloads an audio asset file for Wavesurfer.js browser playback."""
  stmt = select(AudioAsset).where(AudioAsset.id == asset_id)
  result = await db.execute(stmt)
  asset = result.scalar_one_or_none()

  if not asset:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Audio asset '{asset_id}' not found.",
    )

  file_path = Path(asset.file_path)
  if not file_path.is_file():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Audio file '{asset.filename}' does not exist on disk.",
    )

  return FileResponse(
      path=file_path,
      media_type="audio/wav",
      filename=asset.filename,
  )


@router.post("/master", response_model=AudioMasteringResponse)
async def master_audio_asset(
    payload: AudioMasteringRequest,
    db: AsyncSession = Depends(get_db),
) -> AudioMasteringResponse:
  """Applies interactive DSP post-processing mastering (Warm EQ, Reverb, Compression, BGM ducking) to an audio asset."""
  stmt = select(AudioAsset).where(AudioAsset.id == payload.asset_id)
  result = await db.execute(stmt)
  asset = result.scalar_one_or_none()

  if not asset:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Audio asset '{payload.asset_id}' not found.",
    )

  source_path = Path(asset.file_path)
  if not source_path.is_file():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Audio file for asset '{payload.asset_id}' does not exist on disk.",
    )

  try:
    voice_audio, sr = sf.read(str(source_path), dtype="float32")
  except Exception as exc:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to read audio asset: {exc}",
    ) from exc

  # Speed adjustment if requested != 1.0
  if abs(payload.speed - 1.0) > 0.01:
    orig_len = len(voice_audio)
    target_len = int(orig_len / payload.speed)
    voice_audio = scipy.signal.resample(voice_audio, target_len).astype(
        np.float32
    )

  # Optional BGM accompaniment
  bgm_audio: np.ndarray | None = None
  if payload.bgm_preset_id:
    duration = len(voice_audio) / float(sr)
    bgm_audio = generate_synthetic_bgm(payload.bgm_preset_id, duration, sr)

  dsp_params = AudioDSPParams(
      enable_warm_eq=True,
      enable_reverb=payload.reverb_wet > 0.0,
      enable_compression=payload.enable_compression,
      eq_warmth_db=payload.warmth_db,
      eq_air_db=payload.air_db,
      reverb_room_size=payload.room_size,
      reverb_wet=payload.reverb_wet,
      compressor_threshold_db=payload.compressor_threshold_db,
      target_peak_db=-1.0,
  )

  # Run mastering chain
  mastered_audio = audio_dsp.mix_and_master(
      voice_audio=voice_audio,
      bgm_audio=bgm_audio,
      sample_rate=sr,
      bgm_volume=payload.bgm_volume,
      ducking_depth_db=payload.ducking_depth_db,
      dsp_params=dsp_params,
  )

  # Save to disk
  mastered_bytes = audio_dsp.audio_to_wav_bytes(mastered_audio, sr)
  pid_str = str(asset.project_id or "default")[:8]
  aid_str = str(payload.asset_id)[:6]
  mastered_filename = f"mastered_{pid_str}_{aid_str}.wav"
  file_id, safe_path, size_bytes, _ = await storage_service.save_file(
      content=mastered_bytes,
      filename=mastered_filename,
      category="temp",
  )

  new_duration = round(len(mastered_audio) / float(sr), 3)

  # Record in DB
  new_asset = AudioAsset(
      project_id=asset.project_id,
      filename=safe_path.name,
      file_path=str(safe_path),
      file_size=size_bytes,
      duration=new_duration,
      sample_rate=sr,
      channels=1,
      mime_type="audio/wav",
      asset_type="mastered",
  )
  db.add(new_asset)
  await db.commit()
  await db.refresh(new_asset)

  return AudioMasteringResponse(
      asset_id=str(new_asset.id),
      project_id=str(new_asset.project_id or asset.project_id or ""),
      filename=str(new_asset.filename),
      duration=float(new_duration),
      sample_rate=int(sr),
      stream_url=f"/api/v1/audio/assets/{new_asset.id}/stream",
      status="mastered",
  )


@router.post("/trim-silence", response_model=AudioMasteringResponse)
async def trim_audio_silence(
    payload: AudioTrimRequest,
    db: AsyncSession = Depends(get_db),
) -> AudioMasteringResponse:
  """Trims leading and trailing silence from an audio asset using energy VAD."""
  stmt = select(AudioAsset).where(AudioAsset.id == payload.asset_id)
  result = await db.execute(stmt)
  asset = result.scalar_one_or_none()

  if not asset:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Audio asset '{payload.asset_id}' not found.",
    )

  source_path = Path(asset.file_path)
  if not source_path.is_file():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Audio file for asset '{payload.asset_id}' not found on disk.",
    )

  try:
    audio_data, sr = sf.read(str(source_path), dtype="float32")
    trimmed = voice_preprocessor.trim_silence(
        audio=audio_data,
        sample_rate=sr,
        threshold_db=payload.threshold_db,
    )
    trimmed_bytes = audio_dsp.audio_to_wav_bytes(trimmed, sr)
  except Exception as exc:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Failed to trim audio: {exc}",
    ) from exc

  pid_str = str(asset.project_id or "default")[:8]
  aid_str = str(payload.asset_id)[:6]
  trimmed_filename = f"trimmed_{pid_str}_{aid_str}.wav"
  file_id, safe_path, size_bytes, _ = await storage_service.save_file(
      content=trimmed_bytes,
      filename=trimmed_filename,
      category="temp",
  )

  new_duration = round(len(trimmed) / float(sr), 3)

  new_asset = AudioAsset(
      project_id=asset.project_id,
      filename=safe_path.name,
      file_path=str(safe_path),
      file_size=size_bytes,
      duration=new_duration,
      sample_rate=sr,
      channels=1,
      mime_type="audio/wav",
      asset_type="mastered",
  )
  db.add(new_asset)
  await db.commit()
  await db.refresh(new_asset)

  return AudioMasteringResponse(
      asset_id=new_asset.id,
      project_id=new_asset.project_id,
      filename=new_asset.filename,
      duration=float(new_duration),
      sample_rate=int(sr),
      stream_url=f"/api/v1/audio/assets/{new_asset.id}/stream",
      status="trimmed",
  )
