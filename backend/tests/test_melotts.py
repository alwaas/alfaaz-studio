"""Unit tests for MeloTTS Neural Speech Synthesis Adapter."""

import pytest

from app.core.exceptions import AudioProcessingError
from app.services.tts.factory import tts_factory
from app.services.tts.melo_adapter import MeloTTSProvider


@pytest.mark.asyncio
async def test_melotts_synthesis_basic() -> None:
    """Verifies baseline Urdu speech synthesis with MeloTTS adapter."""
    provider = MeloTTSProvider(device="cpu")
    text = "کوئی امید بر نہیں آتی کوئی صورت نظر نہیں آتی"

    result = await provider.synthesize(text=text, speed=1.0)

    assert result.sample_rate == 22050
    assert result.duration > 0.5
    assert len(result.audio_bytes) > 1000
    assert result.audio_bytes[:4] == b"RIFF"
    assert result.audio_bytes[8:12] == b"WAVE"

    # Verify word timestamps
    assert len(result.word_timestamps) == len(text.split())
    assert result.word_timestamps[0]["word"] == "کوئی"

    # Verify metadata and MIT license
    meta = result.metadata
    assert meta["engine"] == "melotts"
    assert meta["model"] == "melo-tts-urdu"
    assert meta["commercial_allowed"] is True
    assert meta["license"] == "MIT"
    assert meta["sample_rate"] == 22050


@pytest.mark.asyncio
async def test_melotts_speakers_and_speed() -> None:
    """Verifies speaker selection and playback rate adjustments."""
    provider = MeloTTSProvider(device="cpu")
    text = "مرگ ناگہاں کا ہے غم کیا"

    res_male = await provider.synthesize(text=text, voice="ur-poet-male", speed=1.0)
    assert res_male.metadata["speaker"] == "ur-poet-male"

    res_female = await provider.synthesize(text=text, voice="ur-poet-female", speed=1.0)
    assert res_female.metadata["speaker"] == "ur-poet-female"

    res_fast = await provider.synthesize(text=text, speed=1.8)
    assert res_fast.duration < res_male.duration


@pytest.mark.asyncio
async def test_melotts_empty_text_error() -> None:
    """Verifies empty string raises AudioProcessingError."""
    provider = MeloTTSProvider(device="cpu")
    with pytest.raises(AudioProcessingError):
        await provider.synthesize(text="")


def test_melotts_factory_resolution() -> None:
    """Verifies that TTSProviderFactory correctly provides MeloTTSProvider."""
    tts_factory.clear_cache()
    provider = tts_factory.get_provider("melotts")
    assert isinstance(provider, MeloTTSProvider)

