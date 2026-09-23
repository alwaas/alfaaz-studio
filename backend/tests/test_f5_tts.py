"""Unit tests for F5-TTS Neural Speech Synthesis Adapter."""

import io
from pathlib import Path
import tempfile
import numpy as np
import pytest
import soundfile as sf  # type: ignore[import-untyped]

from app.core.exceptions import AudioProcessingError
from app.services.tts.f5_adapter import F5TTSProvider
from app.services.tts.factory import tts_factory


@pytest.mark.asyncio
async def test_f5_tts_synthesis_basic() -> None:
    """Verifies baseline Urdu speech synthesis with F5-TTS adapter."""
    provider = F5TTSProvider(device="cpu")
    text = "ستاروں سے آگے جہاں اور بھی ہیں"

    result = await provider.synthesize(text=text, speed=1.0)

    assert result.sample_rate == 24000
    assert result.duration > 0.5
    assert len(result.audio_bytes) > 1000
    assert result.audio_bytes[:4] == b"RIFF"
    assert result.audio_bytes[8:12] == b"WAVE"

    # Verify word timestamps
    assert len(result.word_timestamps) == len(text.split())
    first_word = result.word_timestamps[0]
    assert first_word["word"] == "ستاروں"
    assert first_word["start_time"] == 0.0

    # Verify metadata and personal-use license attribution
    meta = result.metadata
    assert meta["engine"] == "f5-tts"
    assert meta["model"] == "f5-tts-urdu"
    assert meta["commercial_allowed"] is False
    assert "CC-BY-NC-4.0" in meta["license"]
    assert meta["sample_rate"] == 24000


@pytest.mark.asyncio
async def test_f5_tts_speed_and_pitch() -> None:
    """Verifies speed scaling and pitch parameters for F5-TTS."""
    provider = F5TTSProvider(device="cpu")
    text = "دل ناداں تجھے ہوا کیا ہے"

    res_normal = await provider.synthesize(text=text, speed=1.0)
    res_fast = await provider.synthesize(text=text, speed=1.6)
    res_slow = await provider.synthesize(text=text, speed=0.7)

    assert res_fast.duration < res_normal.duration
    assert res_slow.duration > res_normal.duration

    # Pitch parameter
    res_pitch = await provider.synthesize(text=text, speed=1.0, pitch=0.5)
    assert res_pitch.metadata["pitch"] == 0.5


@pytest.mark.asyncio
async def test_f5_tts_voice_cloning_reference() -> None:
    """Verifies voice reference cloning integration in F5-TTS."""
    provider = F5TTSProvider(device="cpu")
    text = "ہزاروں خواہشیں ایسی کہ ہر خواہش پہ دم نکلے"

    # Create synthetic reference audio (3.0s at 16000 Hz)
    sr = 16000
    t = np.linspace(0, 3.0, int(3.0 * sr), endpoint=False)
    synthetic_ref = 0.5 * np.sin(2.0 * np.pi * 220.0 * t).astype(np.float32)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, synthetic_ref, sr, subtype="PCM_16")
        ref_path = Path(tmp.name)

    try:
        result = await provider.synthesize(
            text=text,
            reference_audio=str(ref_path),
            speed=1.0,
        )

        assert result.metadata["cloned"] is True
        assert result.metadata["reference_duration"] is not None
        assert result.metadata["reference_duration"] > 1.0
        assert result.sample_rate == 24000
    finally:
        ref_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_f5_tts_empty_text_error() -> None:
    """Verifies empty string error handling."""
    provider = F5TTSProvider(device="cpu")
    with pytest.raises(AudioProcessingError):
        await provider.synthesize(text="   ")


def test_f5_factory_resolution() -> None:
    """Verifies that TTSProviderFactory correctly provides F5TTSProvider."""
    tts_factory.clear_cache()
    provider = tts_factory.get_provider("f5-tts")
    assert isinstance(provider, F5TTSProvider)

