"""Unit tests for Voice Cloning Audio Preprocessor."""

import io
from pathlib import Path
import tempfile
import numpy as np
import pytest
import soundfile as sf  # type: ignore[import-untyped]

from app.core.exceptions import AudioProcessingError
from app.services.tts.voice_cloning import (
    VoiceCloningPreprocessor,
    VoiceCloningReference,
    voice_preprocessor,
)


def test_stereo_to_mono_conversion() -> None:
    """Verifies multi-channel stereo conversion to single channel mono."""
    # 2D stereo array (samples, 2)
    left = np.full(100, 0.4, dtype=np.float32)
    right = np.full(100, 0.6, dtype=np.float32)
    stereo = np.column_stack((left, right))

    mono = VoiceCloningPreprocessor.to_mono(stereo)
    assert mono.ndim == 1
    assert len(mono) == 100
    assert np.allclose(mono, 0.5, atol=1e-5)

    # 1D array remains unmodified
    single = np.full(50, 0.3, dtype=np.float32)
    mono_single = VoiceCloningPreprocessor.to_mono(single)
    assert mono_single.ndim == 1
    assert len(mono_single) == 50


def test_audio_resampling() -> None:
    """Verifies polyphase resampling between different sampling rates."""
    sr_orig = 16000
    sr_target = 24000
    duration = 1.0

    t = np.linspace(0, duration, int(sr_orig * duration), endpoint=False)
    sine = np.sin(2.0 * np.pi * 440.0 * t).astype(np.float32)

    resampled = VoiceCloningPreprocessor.resample(sine, sr_orig, sr_target)
    assert len(resampled) == int(sr_target * duration)
    assert resampled.dtype == np.float32


def test_silence_trimming() -> None:
    """Verifies VAD silence trimming on leading and trailing silence."""
    sr = 24000
    silence_len = int(0.5 * sr)
    speech_len = int(1.0 * sr)

    silence = np.zeros(silence_len, dtype=np.float32)
    t = np.linspace(0, 1.0, speech_len, endpoint=False)
    speech = (0.7 * np.sin(2.0 * np.pi * 300.0 * t)).astype(np.float32)

    audio_with_silence = np.concatenate((silence, speech, silence))
    trimmed = VoiceCloningPreprocessor.trim_silence(audio_with_silence, sr, threshold_db=-30.0)

    # Trimmed audio should be significantly shorter than full audio with 1s of silence
    assert len(trimmed) < len(audio_with_silence)
    assert len(trimmed) >= speech_len


def test_loudness_normalization() -> None:
    """Verifies peak ceiling normalization."""
    low_audio = np.array([0.05, -0.05, 0.08, -0.08], dtype=np.float32)
    normalized = VoiceCloningPreprocessor.normalize_loudness(low_audio, target_peak_db=-1.0)

    expected_peak = 10.0 ** (-1.0 / 20.0)
    assert np.isclose(np.max(np.abs(normalized)), expected_peak, atol=1e-3)


def test_end_to_end_preprocessing_pipeline() -> None:
    """Verifies end-to-end preprocessing pipeline on synthetic WAV input."""
    sr = 22050
    t = np.linspace(0, 4.0, int(4.0 * sr), endpoint=False)
    samples = (0.5 * np.sin(2.0 * np.pi * 200.0 * t)).astype(np.float32)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, samples, sr, subtype="PCM_16")
        wav_path = Path(tmp.name)

    try:
        ref = voice_preprocessor.preprocess(wav_path, target_sr=24000)
        assert isinstance(ref, VoiceCloningReference)
        assert ref.sample_rate == 24000
        assert ref.channels == 1
        assert ref.duration > 2.0
        assert ref.duration <= 4.0

        wav_bytes = ref.to_wav_bytes()
        assert wav_bytes[:4] == b"RIFF"

        # Test save
        out_path = wav_path.parent / f"preprocessed_{wav_path.name}"
        saved_path = ref.save(out_path)
        assert saved_path.is_file()
        saved_path.unlink(missing_ok=True)
    finally:
        wav_path.unlink(missing_ok=True)


def test_duration_boundary_errors() -> None:
    """Verifies minimum and maximum duration constraints."""
    sr = 24000
    # Too short audio (0.3s)
    short_audio = np.zeros(int(0.3 * sr), dtype=np.float32)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        sf.write(tmp.name, short_audio, sr, subtype="PCM_16")
        tmp_path = Path(tmp.name)

    try:
        with pytest.raises(AudioProcessingError):
            voice_preprocessor.preprocess(tmp_path, min_duration=1.0)
    finally:
        tmp_path.unlink(missing_ok=True)

