"""Unit tests for MockTTSProvider and TTSProviderFactory."""

import io

import pytest
import soundfile as sf  # type: ignore[import-untyped]

from app.services.tts.factory import tts_factory
from app.services.tts.mock_provider import MockTTSProvider
from app.services.tts.provider import TTSProvider, TTSResult


@pytest.mark.asyncio
async def test_mock_tts_synthesis_basic() -> None:
    """Test basic 440Hz harmonic synthesis with default parameters."""
    provider = MockTTSProvider(default_sample_rate=24000)
    assert isinstance(provider, TTSProvider)

    text = "دل سے جو بات نکلتی ہے اثر رکھتی ہے"
    result: TTSResult = await provider.synthesize(text=text, speed=1.0)

    assert isinstance(result, TTSResult)
    assert result.sample_rate == 24000
    assert result.duration > 0.0
    assert len(result.audio_bytes) > 0
    assert result.metadata["engine"] == "mock"
    assert result.metadata["frequency_hz"] == 440.0
    assert result.metadata["speed"] == 1.0

    # Verify audio bytes are valid 16-bit PCM WAV
    buffer = io.BytesIO(result.audio_bytes)
    data, sample_rate = sf.read(buffer)
    assert sample_rate == 24000
    assert len(data) > 0


@pytest.mark.asyncio
async def test_mock_tts_variable_duration_and_bounds() -> None:
    """Test explicit duration support bounded between 1.0s and 300.0s."""
    provider = MockTTSProvider()

    # Short duration
    short_res = await provider.synthesize(text="شعر", duration=2.5)
    assert short_res.duration == 2.5

    # Boundary lower clamp (min 1.0s)
    min_res = await provider.synthesize(text="شعر", duration=0.2)
    assert min_res.duration == 1.0

    # Boundary upper clamp (max 300.0s)
    max_res = await provider.synthesize(text="طویل نظم", duration=500.0)
    assert max_res.duration == 300.0


@pytest.mark.asyncio
async def test_mock_tts_speed_scaling() -> None:
    """Test that speed alters duration proportionally and is clamped between 0.5x and 2.0x."""
    provider = MockTTSProvider()
    text = "ستاروں سے آگے جہاں اور بھی ہیں"

    normal_res = await provider.synthesize(text=text, speed=1.0)
    fast_res = await provider.synthesize(text=text, speed=2.0)
    slow_res = await provider.synthesize(text=text, speed=0.5)

    # Fast recitation should take less time than slow recitation
    assert fast_res.duration < normal_res.duration
    assert slow_res.duration > normal_res.duration

    # Speed clamping tests
    assert MockTTSProvider.validate_speed(0.1) == 0.5
    assert MockTTSProvider.validate_speed(3.5) == 2.0
    assert MockTTSProvider.validate_speed(1.25) == 1.25


@pytest.mark.asyncio
async def test_mock_tts_word_timestamps() -> None:
    """Test generated word alignments and time continuity."""
    provider = MockTTSProvider()
    text = "ہزاروں خواہشیں ایسی کہ ہر خواہش پہ دم نکلے"
    words = text.split()

    result = await provider.synthesize(text=text, speed=1.0)
    timestamps = result.word_timestamps

    assert len(timestamps) == len(words)

    # Check ascending sequence and proper bounds
    prev_end = 0.0
    for ts, word in zip(timestamps, words, strict=False):
        assert ts["word"] == word
        assert ts["start_time"] >= prev_end or ts["start_time"] >= 0.0
        assert ts["end_time"] > ts["start_time"]
        assert ts["end_time"] <= result.duration + 0.01
        prev_end = ts["start_time"]


def test_tts_factory_caching_and_fallback() -> None:
    """Test that TTSProviderFactory caches instances and handles unknown engines gracefully."""
    tts_factory.clear_cache()

    provider1 = tts_factory.get_provider("mock")
    provider2 = tts_factory.get_provider("mock")
    assert provider1 is provider2

    # Unrecognized or neural engines in Phase 3 return MockTTSProvider
    fallback_provider = tts_factory.get_provider("unrecognized_engine_xyz")
    assert isinstance(fallback_provider, MockTTSProvider)
