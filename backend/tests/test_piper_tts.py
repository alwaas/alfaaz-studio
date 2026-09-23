"""Unit tests for Piper Neural Speech Synthesis Adapter."""

import pytest

from app.core.exceptions import AudioProcessingError
from app.services.tts.factory import tts_factory
from app.services.tts.piper_adapter import PiperTTSProvider


@pytest.mark.asyncio
async def test_piper_synthesis_basic() -> None:
    """Verifies baseline Urdu speech synthesis with Piper adapter."""
    provider = PiperTTSProvider(device="cpu")
    text = "زندگی سے یہی گلہ ہے مجھے"

    result = await provider.synthesize(text=text, speed=1.0)

    assert result.sample_rate == 22050
    assert result.duration > 0.4
    assert len(result.audio_bytes) > 1000
    assert result.audio_bytes[:4] == b"RIFF"
    assert result.audio_bytes[8:12] == b"WAVE"

    assert len(result.word_timestamps) == len(text.split())
    assert result.word_timestamps[0]["word"] == "زندگی"

    meta = result.metadata
    assert meta["engine"] == "piper"
    assert meta["model"] == "piper-urdu-medium"
    assert meta["commercial_allowed"] is True
    assert meta["license"] == "MIT"


@pytest.mark.asyncio
async def test_piper_speed_and_empty() -> None:
    """Verifies speed adjustments and empty string error."""
    provider = PiperTTSProvider(device="cpu")
    text = "یہ نہ تھی ہماری قسمت کہ وصال یار ہوتا"

    res_normal = await provider.synthesize(text=text, speed=1.0)
    res_fast = await provider.synthesize(text=text, speed=1.5)
    assert res_fast.duration < res_normal.duration

    with pytest.raises(AudioProcessingError):
        await provider.synthesize(text="   ")


def test_piper_factory_resolution() -> None:
    """Verifies that TTSProviderFactory correctly provides PiperTTSProvider."""
    tts_factory.clear_cache()
    provider = tts_factory.get_provider("piper")
    assert isinstance(provider, PiperTTSProvider)
