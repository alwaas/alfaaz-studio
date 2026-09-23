"""Mock TTS Provider implementation generating harmonic audio and synthetic alignments."""

import io
import math
from typing import Any, Optional
import numpy as np
import soundfile as sf  # type: ignore[import-untyped]
from app.services.tts.provider import TTSProvider, TTSResult, WordTimestamp


class MockTTSProvider:
    """
    Deterministic mock TTS provider for testing, local development, and CI/CD.
    Generates a 440Hz sine wave (with subtle musical harmonics) matching text length.
    """

    def __init__(self, default_sample_rate: int = 24000) -> None:
        self.sample_rate = default_sample_rate

    @staticmethod
    def validate_speed(speed: float) -> float:
        """Clamp and validate synthesis speed between 0.5x and 2.0x."""
        return max(0.5, min(2.0, float(speed)))

    @staticmethod
    def calculate_text_duration(text: str, speed: float = 1.0) -> float:
        """
        Estimate spoken duration based on Urdu word and character count.
        Urdu poetry recitation typically averages 2.0 - 2.5 words per second.
        Duration is bounded between 1.0 and 300.0 seconds.
        """
        words = [w for w in text.strip().split() if w]
        word_count = len(words)

        if word_count == 0:
            base_duration = 1.0
        else:
            # Approx 0.45s per word + 0.2s pause between verses/phrases
            base_duration = max(1.0, word_count * 0.45 + (text.count("\n") * 0.5))

        # Adjust duration inversely proportional to speed
        effective_duration = base_duration / speed
        return max(1.0, min(300.0, round(effective_duration, 2)))

    def generate_sine_wave(
        self,
        duration_seconds: float,
        frequency_hz: float = 440.0,
    ) -> np.ndarray:
        """
        Generate a 440Hz sine wave with harmonic overtones and envelope shaping.
        """
        num_samples = int(self.sample_rate * duration_seconds)
        t = np.linspace(0, duration_seconds, num_samples, endpoint=False)

        # Fundamental 440Hz + subtle harmonics (880Hz, 1320Hz)
        waveform = (
            0.6 * np.sin(2 * np.pi * frequency_hz * t)
            + 0.25 * np.sin(2 * np.pi * (frequency_hz * 2) * t)
            + 0.15 * np.sin(2 * np.pi * (frequency_hz * 3) * t)
        )

        # Apply smooth attack and release envelope (20ms ramp)
        ramp_samples = min(int(self.sample_rate * 0.02), num_samples // 4)
        if ramp_samples > 0:
            attack = np.linspace(0.0, 1.0, ramp_samples)
            release = np.linspace(1.0, 0.0, ramp_samples)
            waveform[:ramp_samples] *= attack
            waveform[-ramp_samples:] *= release

        return waveform.astype(np.float32)

    def generate_word_timestamps(
        self,
        text: str,
        total_duration: float,
    ) -> list[dict[str, Any]]:
        """Compute synthetic word alignment timestamps distributed across total duration."""
        words = [w for w in text.strip().split() if w]
        if not words:
            return []

        word_count = len(words)
        slot_duration = total_duration / word_count
        timestamps: list[dict[str, Any]] = []

        current_time = 0.0
        for i, word in enumerate(words):
            start_time = current_time
            # 85% of slot is speech, 15% is inter-word acoustic micro-pause
            end_time = (
                start_time + (slot_duration * 0.85)
                if i < word_count - 1
                else total_duration
            )
            timestamps.append(
                WordTimestamp(
                    word=word,
                    start_time=start_time,
                    end_time=end_time,
                    confidence=0.98,
                ).to_dict()
            )
            current_time += slot_duration

        return timestamps

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 0.0,
        reference_audio: Optional[str] = None,
        duration: Optional[float] = None,
        **kwargs: Any,
    ) -> TTSResult:
        """Synthesize Urdu text into deterministic mock WAV audio."""
        valid_speed = self.validate_speed(speed)

        # Calculate or enforce duration
        if duration is not None:
            effective_duration = max(1.0, min(300.0, float(duration)))
        else:
            effective_duration = self.calculate_text_duration(text, valid_speed)

        # Base frequency modified slightly by pitch (-1.0 to 1.0 maps to 392Hz - 494Hz)
        base_freq = 440.0 * (2.0 ** (pitch * 0.2))

        # Generate audio buffer
        audio_data = self.generate_sine_wave(
            duration_seconds=effective_duration,
            frequency_hz=base_freq,
        )

        # Write to WAV byte stream
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, self.sample_rate, format="WAV", subtype="PCM_16")
        audio_bytes = buffer.getvalue()

        # Word alignments
        timestamps = self.generate_word_timestamps(text, effective_duration)

        return TTSResult(
            audio_bytes=audio_bytes,
            sample_rate=self.sample_rate,
            duration=effective_duration,
            word_timestamps=timestamps,
            metadata={
                "engine": "mock",
                "frequency_hz": round(base_freq, 2),
                "speed": valid_speed,
                "pitch": pitch,
                "voice": voice or "mock_default",
                "word_count": len(timestamps),
                "channels": 1,
                "format": "wav",
            },
        )
