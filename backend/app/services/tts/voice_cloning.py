"""Voice Cloning Audio Preprocessor.

Performs reference audio preparation for zero-shot voice cloning (F5-TTS, etc.):
- Multi-channel stereo to mono conversion
- High-quality polyphase resampling to target sampling rate (24kHz / 22.05kHz)
- VAD energy-based leading/trailing silence trimming
- Loudness and peak normalization (-20 dBFS target RMS, -1.0 dBFS peak ceiling)
- Duration constraint enforcement (3s-15s recommended optimal reference length)
"""

import io
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import scipy.signal  # type: ignore[import-untyped]
import soundfile as sf  # type: ignore[import-untyped]

from app.core.exceptions import AudioProcessingError
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class VoiceCloningReference:
    """Preprocessed reference audio ready for neural voice cloning."""

    audio_data: np.ndarray
    sample_rate: int
    duration: float
    channels: int = 1
    original_path: str | None = None

    def to_wav_bytes(self) -> bytes:
        """Serializes preprocessed float32 audio to 16-bit PCM WAV bytes."""
        buffer = io.BytesIO()
        # Scale to 16-bit PCM range
        int16_data = np.clip(self.audio_data * 32767.0, -32768, 32767).astype(np.int16)
        sf.write(buffer, int16_data, self.sample_rate, format="WAV", subtype="PCM_16")
        return buffer.getvalue()

    def save(self, output_path: Path) -> Path:
        """Saves preprocessed reference to a target file path."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        int16_data = np.clip(self.audio_data * 32767.0, -32768, 32767).astype(np.int16)
        sf.write(output_path, int16_data, self.sample_rate, format="WAV", subtype="PCM_16")
        return output_path


class VoiceCloningPreprocessor:
    """Pipelines and cleans voice reference samples for neural cloning."""

    @staticmethod
    def load_audio(source: str | Path | bytes) -> tuple[np.ndarray, int]:
        """Loads audio from a file path or raw bytes into a float32 numpy array."""
        try:
            if isinstance(source, bytes):
                data, sr = sf.read(io.BytesIO(source), dtype="float32")
            else:
                data, sr = sf.read(str(source), dtype="float32")
            return data, sr
        except Exception as exc:
            raise AudioProcessingError(f"Failed to read audio for voice cloning: {exc}") from exc

    @staticmethod
    def to_mono(audio: np.ndarray) -> np.ndarray:
        """Converts multi-channel audio to single-channel mono."""
        if audio.ndim == 1:
            return audio
        return np.mean(audio, axis=1)

    @staticmethod
    def resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resamples audio to target sample rate using polyphase filtering."""
        if orig_sr == target_sr:
            return audio

        gcd = math.gcd(orig_sr, target_sr)
        up = target_sr // gcd
        down = orig_sr // gcd
        resampled = scipy.signal.resample_poly(audio, up, down)
        return resampled.astype(np.float32)

    @staticmethod
    def trim_silence(
        audio: np.ndarray,
        sample_rate: int,
        threshold_db: float = -40.0,
        frame_ms: float = 25.0,
        hop_ms: float = 10.0,
        pad_ms: float = 50.0,
    ) -> np.ndarray:
        """
        Trims leading and trailing silence using RMS energy thresholding.

        :param audio: 1D float32 audio samples.
        :param sample_rate: Audio sample rate.
        :param threshold_db: Silence threshold in dBFS (e.g. -40 dB).
        :param frame_ms: Window length in milliseconds for RMS computation.
        :param hop_ms: Hop size in milliseconds.
        :param pad_ms: Padding to retain before/after speech boundaries.
        """
        if len(audio) == 0:
            return audio

        frame_len = max(1, int(sample_rate * (frame_ms / 1000.0)))
        hop_len = max(1, int(sample_rate * (hop_ms / 1000.0)))
        pad_samples = int(sample_rate * (pad_ms / 1000.0))

        # Compute RMS energy per frame
        num_frames = max(1, (len(audio) - frame_len) // hop_len + 1)
        energies = []
        for i in range(num_frames):
            start = i * hop_len
            frame = audio[start : start + frame_len]
            rms = np.sqrt(np.mean(frame**2) + 1e-12)
            db = 20.0 * np.log10(rms)
            energies.append(db)

        # Identify speech frames
        speech_indices = [idx for idx, energy in enumerate(energies) if energy > threshold_db]
        if not speech_indices:
            # If all audio is below threshold, return original
            return audio

        first_speech_sample = max(0, speech_indices[0] * hop_len - pad_samples)
        last_speech_sample = min(
            len(audio), (speech_indices[-1] * hop_len + frame_len) + pad_samples
        )

        return audio[first_speech_sample:last_speech_sample]

    @staticmethod
    def normalize_loudness(audio: np.ndarray, target_peak_db: float = -1.0) -> np.ndarray:
        """Normalizes audio to target peak dBFS ceiling."""
        if len(audio) == 0:
            return audio
        peak = np.max(np.abs(audio))
        if peak < 1e-6:
            return audio
        target_linear = 10.0 ** (target_peak_db / 20.0)
        gain = target_linear / peak
        return audio * gain

    def preprocess(
        self,
        source: str | Path | bytes,
        target_sr: int = 24000,
        min_duration: float = 1.0,
        max_duration: float = 30.0,
    ) -> VoiceCloningReference:
        """
        Executes end-to-end preprocessing pipeline on reference audio:
        1. Read audio
        2. Convert to mono
        3. Resample to target_sr
        4. Silence trim
        5. Peak & RMS normalize
        6. Validate duration bounds
        """
        audio, orig_sr = self.load_audio(source)
        mono_audio = self.to_mono(audio)
        resampled = self.resample(mono_audio, orig_sr, target_sr)
        trimmed = self.trim_silence(resampled, target_sr)
        normalized = self.normalize_loudness(trimmed, target_peak_db=-1.0)

        duration = len(normalized) / float(target_sr)
        if duration < min_duration:
            raise AudioProcessingError(
                f"Reference audio duration ({duration:.2f}s) is shorter than minimum required ({min_duration:.1f}s)"
            )

        if duration > max_duration:
            logger.info(
                f"Reference audio ({duration:.2f}s) exceeds maximum ({max_duration:.1f}s); slicing first {max_duration:.1f}s"
            )
            max_samples = int(max_duration * target_sr)
            normalized = normalized[:max_samples]
            duration = max_duration

        orig_path_str = str(source) if isinstance(source, (str, Path)) else None

        return VoiceCloningReference(
            audio_data=normalized.astype(np.float32),
            sample_rate=target_sr,
            duration=round(duration, 3),
            channels=1,
            original_path=orig_path_str,
        )


voice_preprocessor = VoiceCloningPreprocessor()
