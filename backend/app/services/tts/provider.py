"""TTS Provider Protocol and Result Data Structures."""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@dataclass
class WordTimestamp:
    """Timestamp alignment for a single spoken word."""

    word: str
    start_time: float
    end_time: float
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "word": self.word,
            "start_time": round(self.start_time, 3),
            "end_time": round(self.end_time, 3),
            "confidence": round(self.confidence, 3),
        }


@dataclass
class TTSResult:
    """Output structure returned by any TTS provider implementation."""

    audio_bytes: bytes
    sample_rate: int
    duration: float
    word_timestamps: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class TTSProvider(Protocol):
    """Abstract protocol that all TTS synthesis engines must implement."""

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        speed: float = 1.0,
        pitch: float = 0.0,
        reference_audio: str | None = None,
        **kwargs: Any,
    ) -> TTSResult:
        """
        Synthesize text into speech audio with word alignments.

        :param text: Cleaned or normalized Urdu text.
        :param voice: Voice preset identifier or name.
        :param speed: Playback/synthesis speed multiplier (0.5x - 2.0x).
        :param pitch: Pitch modulation adjustment (-1.0 to 1.0).
        :param reference_audio: Path to voice cloning reference audio if supported.
        :return: TTSResult containing WAV bytes and alignment metadata.
        """
        ...
