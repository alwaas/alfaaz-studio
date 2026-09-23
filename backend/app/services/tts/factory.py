"""TTS Provider Factory for instantiating and caching synthesis engines."""

from app.config import settings
from app.core.logging import get_logger
from app.services.tts.mock_provider import MockTTSProvider
from app.services.tts.provider import TTSProvider

logger = get_logger(__name__)


class TTSProviderFactory:
    """Factory creating and caching TTS provider instances."""

    _instances: dict[str, TTSProvider] = {}

    @classmethod
    def get_provider(cls, engine_name: str | None = None) -> TTSProvider:
        """
        Retrieve or instantiate a TTS provider matching engine_name.
        Falls back to MockTTSProvider if requested engine is unavailable.
        """
        engine = (engine_name or settings.DEFAULT_TTS_ENGINE).lower()

        if engine in cls._instances:
            return cls._instances[engine]

        provider: TTSProvider

        match engine:
            case "mock":
                provider = MockTTSProvider(default_sample_rate=settings.SAMPLE_RATE)
            case "f5-tts" | "melotts" | "piper":
                # In Phase 3, default neural adapters fall back gracefully to MockTTSProvider
                logger.info(
                    f"TTS engine '{engine}' requested; utilizing MockTTSProvider harness for Phase 3"
                )
                provider = MockTTSProvider(default_sample_rate=settings.SAMPLE_RATE)
            case _:
                logger.warning(f"Unknown TTS engine '{engine}'; falling back to MockTTSProvider")
                provider = MockTTSProvider(default_sample_rate=settings.SAMPLE_RATE)

        cls._instances[engine] = provider
        return provider

    @classmethod
    def register_provider(cls, engine_name: str, provider: TTSProvider) -> None:
        """Register a custom provider implementation."""
        cls._instances[engine_name.lower()] = provider

    @classmethod
    def clear_cache(cls) -> None:
        """Clear cached provider instances."""
        cls._instances.clear()


tts_factory = TTSProviderFactory
