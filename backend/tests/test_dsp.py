"""Unit tests for Cinematic Audio Post-Processing DSP Chain."""

import numpy as np

from app.services.dsp import AudioDSPChain, AudioDSPParams, audio_dsp


def test_biquad_peaking_design() -> None:
    """Verifies biquad peaking equalizer filter coefficient generation."""
    b, a = AudioDSPChain.design_biquad_peaking(f0=200.0, gain_db=3.0, q=1.0, fs=24000)
    assert len(b) == 3
    assert len(a) == 3
    assert np.isfinite(b).all()
    assert np.isfinite(a).all()


def test_apply_warm_eq() -> None:
    """Verifies warm vocal EQ frequency shaping."""
    sr = 24000
    duration = 0.5
    t = np.linspace(0, duration, int(duration * sr), endpoint=False)
    # Composite signal: 180 Hz (warmth band) + 1000 Hz
    signal = (
        0.3 * np.sin(2.0 * np.pi * 180.0 * t) + 0.3 * np.sin(2.0 * np.pi * 1000.0 * t)
    ).astype(np.float32)

    eq_audio = AudioDSPChain.apply_warm_eq(signal, sr, warmth_db=3.0, mud_cut_db=-2.0, air_db=2.0)
    assert len(eq_audio) == len(signal)
    assert eq_audio.dtype == np.float32
    assert not np.isnan(eq_audio).any()
    assert not np.array_equal(eq_audio, signal)

    # Empty array handling
    empty = np.array([], dtype=np.float32)
    assert len(AudioDSPChain.apply_warm_eq(empty, sr)) == 0


def test_apply_reverb() -> None:
    """Verifies algorithmic reverb room simulation."""
    sr = 24000
    impulse = np.zeros(int(0.5 * sr), dtype=np.float32)
    impulse[0] = 1.0  # Unit impulse

    # Dry only
    dry = AudioDSPChain.apply_reverb(impulse, sr, wet_mix=0.0)
    assert np.allclose(dry, impulse)

    # Wet reverb
    reverbed = AudioDSPChain.apply_reverb(impulse, sr, decay_time=1.0, wet_mix=0.25, room_size=0.5)
    assert len(reverbed) == len(impulse)
    # Reverbed signal should have energy after the initial impulse
    tail_energy = np.sum(reverbed[1000:] ** 2)
    assert tail_energy > 1e-6


def test_apply_compression() -> None:
    """Verifies dynamic compressor peak containment and dynamic range reduction."""
    sr = 24000
    # Two-tone signal: loud portion followed by quiet portion
    t = np.linspace(0, 0.5, int(0.5 * sr), endpoint=False)
    loud = 0.9 * np.sin(2.0 * np.pi * 300.0 * t)
    quiet = 0.1 * np.sin(2.0 * np.pi * 300.0 * t)
    signal = np.concatenate((loud, quiet)).astype(np.float32)

    compressed = AudioDSPChain.apply_compression(
        signal,
        sr,
        threshold_db=-14.0,
        ratio=4.0,
        attack_ms=5.0,
        release_ms=50.0,
        makeup_gain_db=0.0,
    )

    assert len(compressed) == len(signal)
    # Loud portion should be attenuated
    loud_compressed_peak = np.max(np.abs(compressed[: len(loud)]))
    assert loud_compressed_peak < np.max(np.abs(loud))


def test_duck_bgm() -> None:
    """Verifies dynamic sidechain ducking of background music under speech."""
    sr = 24000
    duration = 2.0
    total_samples = int(duration * sr)

    # Speech is active between 0.5s and 1.5s
    voice = np.zeros(total_samples, dtype=np.float32)
    speech_start = int(0.5 * sr)
    speech_end = int(1.5 * sr)
    t_speech = np.linspace(0, 1.0, speech_end - speech_start, endpoint=False)
    voice[speech_start:speech_end] = 0.7 * np.sin(2.0 * np.pi * 200.0 * t_speech)

    # Constant amplitude background music
    bgm = np.full(total_samples, 0.5, dtype=np.float32)

    ducked = AudioDSPChain.duck_bgm(
        voice=voice,
        bgm=bgm,
        sample_rate=sr,
        ducking_depth_db=-12.0,
        threshold_db=-30.0,
    )

    assert len(ducked) == total_samples
    # Average level during speech should be lower than during silence
    silent_period_mean = np.mean(np.abs(ducked[: int(0.3 * sr)]))
    speech_period_mean = np.mean(np.abs(ducked[int(0.8 * sr) : int(1.2 * sr)]))
    assert speech_period_mean < silent_period_mean


def test_master_speech_and_mix_and_master() -> None:
    """Verifies complete vocal mastering and multi-track mixing pipeline."""
    sr = 24000
    duration = 1.0
    t = np.linspace(0, duration, int(duration * sr), endpoint=False)
    voice = (0.5 * np.sin(2.0 * np.pi * 180.0 * t)).astype(np.float32)
    bgm = (0.2 * np.sin(2.0 * np.pi * 440.0 * t)).astype(np.float32)

    params = AudioDSPParams(
        enable_warm_eq=True,
        enable_reverb=True,
        enable_compression=True,
        reverb_wet=0.10,
    )

    # Master solo voice
    mastered = audio_dsp.master_speech(voice, sr, params)
    assert len(mastered) == len(voice)
    peak = np.max(np.abs(mastered))
    expected_peak = 10.0 ** (-1.0 / 20.0)
    assert np.isclose(peak, expected_peak, atol=1e-2)

    # Mix voice + BGM
    mixed = audio_dsp.mix_and_master(voice, bgm, sr, dsp_params=params)
    assert len(mixed) == len(voice)
    assert np.max(np.abs(mixed)) <= 1.0

    # Serialization to WAV
    wav_bytes = audio_dsp.audio_to_wav_bytes(mixed, sr)
    assert len(wav_bytes) > 1000
    assert wav_bytes[:4] == b"RIFF"
    assert wav_bytes[8:12] == b"WAVE"
