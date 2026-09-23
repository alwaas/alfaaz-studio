"""TTS Services module."""

from app.services.tts.f5_adapter import F5TTSProvider
from app.services.tts.factory import tts_factory
from app.services.tts.melo_adapter import MeloTTSProvider
from app.services.tts.mock_provider import MockTTSProvider
from app.services.tts.model_manager import HardwareManager, ModelManager, model_manager
from app.services.tts.piper_adapter import PiperTTSProvider
from app.services.tts.provider import TTSProvider, TTSResult, WordTimestamp
from app.services.tts.voice_cloning import VoiceCloningReference, voice_preprocessor

__all__ = [
    "TTSProvider",
    "TTSResult",
    "WordTimestamp",
    "MockTTSProvider",
    "F5TTSProvider",
    "MeloTTSProvider",
    "PiperTTSProvider",
    "tts_factory",
    "model_manager",
    "ModelManager",
    "HardwareManager",
    "voice_preprocessor",
    "VoiceCloningReference",
]
