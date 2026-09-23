"""TTS Services module."""

from app.services.tts.factory import tts_factory
from app.services.tts.mock_provider import MockTTSProvider
from app.services.tts.provider import TTSProvider, TTSResult, WordTimestamp

__all__ = [
    "TTSProvider",
    "TTSResult",
    "WordTimestamp",
    "MockTTSProvider",
    "tts_factory",
]
