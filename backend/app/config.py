"""Application configuration module."""

from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Application
    APP_NAME: str = "AlfaazStudio"
    APP_ENV: str = "development"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "debug", "development")
        return bool(v)

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./alfaaz.db"

    # Compute
    DEVICE: str = "auto"
    CUDA_VISIBLE_DEVICES: str = "0"
    TORCH_NUM_THREADS: int = 4

    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODEL_DIR: Path = Field(default_factory=lambda: Path("./models"))
    OUTPUT_DIR: Path = Field(default_factory=lambda: Path("./outputs"))
    TEMP_DIR: Path = Field(default_factory=lambda: Path("./temp"))
    DATA_DIR: Path = Field(default_factory=lambda: Path("./data"))

    # TTS Settings
    DEFAULT_TTS_ENGINE: str = "f5-tts"
    FALLBACK_TTS_ENGINE: str = "mock"
    SAMPLE_RATE: int = 24000

    # Video Settings
    VIDEO_WIDTH: int = 1080
    VIDEO_HEIGHT: int = 1920
    VIDEO_FPS: int = 30
    DEFAULT_FONT_NAME: str = "Jameel Noori Nastaleeq"
    FALLBACK_FONT_NAME: str = "Noto Nastaliq Urdu"

    # Concurrency & Logging
    MAX_CONCURRENT_RENDERS: int = 2
    LOG_LEVEL: str = "INFO"

    def get_resolved_path(self, path: Path) -> Path:
        """Resolve path relative to BASE_DIR if not absolute."""
        if path.is_absolute():
            return path
        return (self.BASE_DIR / path).resolve()

    @property
    def resolved_model_dir(self) -> Path:
        return self.get_resolved_path(self.MODEL_DIR)

    @property
    def resolved_output_dir(self) -> Path:
        return self.get_resolved_path(self.OUTPUT_DIR)

    @property
    def resolved_temp_dir(self) -> Path:
        return self.get_resolved_path(self.TEMP_DIR)

    @property
    def resolved_data_dir(self) -> Path:
        return self.get_resolved_path(self.DATA_DIR)


settings = Settings()
