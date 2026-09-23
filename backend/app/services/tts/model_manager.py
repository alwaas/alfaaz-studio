"""Model Manager and Hardware Selection for Neural Speech Synthesis.

Handles CUDA detection, CPU fallback, SHA-256 weight verification, model caching,
and out-of-memory (OOM) recovery for AlfaazStudio TTS models.
"""

import hashlib
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import psutil  # type: ignore[import-untyped]

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ModelMetadata:
    """Metadata describing a registered TTS neural model."""

    name: str
    engine: str
    version: str
    description: str
    license_type: str
    commercial_allowed: bool
    expected_sample_rate: int
    local_dir: Path
    weights_filename: str | None = None
    expected_sha256: str | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def weights_path(self) -> Path | None:
        if self.weights_filename:
            return self.local_dir / self.weights_filename
        return None


class HardwareManager:
    """Detects available computing hardware and manages device allocation."""

    @staticmethod
    def detect_device() -> str:
        """
        Detects primary compute device.
        Returns 'cuda' if NVIDIA GPU is present and torch detects CUDA, otherwise 'cpu'.
        """
        try:
            import torch  # type: ignore[import-not-found]

            if torch.cuda.is_available():
                return "cuda"
        except (ImportError, Exception):
            pass
        return "cpu"

    @classmethod
    def get_device_info(cls) -> dict[str, Any]:
        """Returns comprehensive device telemetry including memory metrics."""
        device = cls.detect_device()
        vm = psutil.virtual_memory()

        info: dict[str, Any] = {
            "device": device,
            "cpu_count": psutil.cpu_count(logical=True) or 1,
            "cpu_percent": psutil.cpu_percent(interval=None),
            "ram_total_mb": round(vm.total / (1024 * 1024), 1),
            "ram_available_mb": round(vm.available / (1024 * 1024), 1),
            "cuda_available": device == "cuda",
            "gpu_name": None,
            "vram_total_mb": None,
            "vram_free_mb": None,
        }

        if device == "cuda":
            try:
                import torch  # type: ignore[import-not-found]

                gpu_idx = torch.cuda.current_device()
                props = torch.cuda.get_device_properties(gpu_idx)
                info["gpu_name"] = props.name
                total_vram = props.total_memory
                allocated_vram = torch.cuda.memory_allocated(gpu_idx)
                reserved_vram = torch.cuda.memory_reserved(gpu_idx)
                free_vram = total_vram - reserved_vram

                info["vram_total_mb"] = round(total_vram / (1024 * 1024), 1)
                info["vram_free_mb"] = round(free_vram / (1024 * 1024), 1)
                info["vram_allocated_mb"] = round(allocated_vram / (1024 * 1024), 1)
            except Exception as exc:
                logger.warning(f"Error querying CUDA telemetry: {exc}")

        return info

    @classmethod
    def get_precision(cls, device: str | None = None) -> str:
        """Determines optimal inference precision (fp16/bf16 on CUDA, fp32 on CPU)."""
        target_device = device or cls.detect_device()
        if target_device == "cuda":
            try:
                import torch  # type: ignore[import-not-found]

                if torch.cuda.is_bf16_supported():
                    return "bfloat16"
                return "float16"
            except Exception:
                return "float16"
        return "float32"


class ModelManager:
    """
    Manages neural model lifecycle: registration, SHA-256 checksum verification,
    memory caching, and hardware failover.
    """

    def __init__(self, models_root: Path | None = None) -> None:
        self.models_root = models_root or settings.resolved_model_dir
        self._cache: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._registry: dict[str, ModelMetadata] = {}
        self._register_default_models()

    def _register_default_models(self) -> None:
        """Registers supported Urdu neural speech synthesis models."""
        self.register_model(
            ModelMetadata(
                name="f5-tts-urdu",
                engine="f5-tts",
                version="1.0.0",
                description="F5-TTS Non-autoregressive Flow Matching speech synthesizer with voice cloning",
                license_type="CC-BY-NC-4.0",
                commercial_allowed=False,  # Personal use only
                expected_sample_rate=24000,
                local_dir=self.models_root / "f5_tts",
                weights_filename="model_1200000.safetensors",
                expected_sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                tags=["neural", "diffusion", "voice-cloning", "urdu"],
            )
        )

        self.register_model(
            ModelMetadata(
                name="melo-tts-urdu",
                engine="melotts",
                version="0.1.2",
                description="MeloTTS Fast multilingual multi-speaker synthesis engine",
                license_type="MIT",
                commercial_allowed=True,
                expected_sample_rate=22050,
                local_dir=self.models_root / "melo_tts",
                weights_filename="checkpoint.pth",
                tags=["neural", "vits", "fast", "urdu"],
            )
        )

        self.register_model(
            ModelMetadata(
                name="piper-urdu-medium",
                engine="piper",
                version="1.0.0",
                description="Piper lightweight ONNX fast speech synthesizer",
                license_type="MIT",
                commercial_allowed=True,
                expected_sample_rate=22050,
                local_dir=self.models_root / "piper",
                weights_filename="ur_PK-medium.onnx",
                tags=["onnx", "lightweight", "low-latency", "urdu"],
            )
        )

    def register_model(self, meta: ModelMetadata) -> None:
        """Registers a model metadata specification."""
        self._registry[meta.name] = meta
        if meta.engine not in self._registry:
            self._registry[meta.engine] = meta

    def get_metadata(self, identifier: str) -> ModelMetadata | None:
        """Look up model metadata by name or engine."""
        return self._registry.get(identifier.lower())

    def list_models(self) -> list[ModelMetadata]:
        """List all unique registered models."""
        unique_models = {meta.name: meta for meta in self._registry.values()}
        return list(unique_models.values())

    @staticmethod
    def compute_sha256(file_path: Path) -> str:
        """Computes SHA-256 hash of a file in 64KB blocks."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(65536), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def verify_checksum(self, file_path: Path, expected_sha256: str) -> bool:
        """
        Verifies file checksum against expected SHA-256.
        Returns True if matching, False otherwise.
        """
        if not file_path.is_file():
            logger.error(f"Cannot verify checksum: file does not exist at {file_path}")
            return False
        computed = self.compute_sha256(file_path)
        matches = computed.lower() == expected_sha256.lower()
        if not matches:
            logger.warning(
                f"Checksum mismatch for {file_path.name}: expected {expected_sha256}, got {computed}"
            )
        return matches

    def is_model_available(self, identifier: str) -> bool:
        """Checks if the model directory and weights file exist on disk."""
        meta = self.get_metadata(identifier)
        if not meta or not meta.weights_path:
            return False
        return meta.weights_path.is_file()

    def get_or_load_model(
        self,
        identifier: str,
        loader_fn: Callable[[str, str], Any],
        device: str | None = None,
    ) -> Any:
        """
        Thread-safe loader with caching and OOM automatic fallback to CPU.

        :param identifier: Model name or engine key.
        :param loader_fn: Callable receiving (weights_path, device) returning model object.
        :param device: Target device ('cuda' or 'cpu'), defaults to hardware auto-detection.
        """
        target_device = device or HardwareManager.detect_device()
        cache_key = f"{identifier}:{target_device}"

        with self._lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

            meta = self.get_metadata(identifier)
            weights_path_str = str(meta.weights_path) if meta and meta.weights_path else ""

            try:
                logger.info(f"Loading model '{identifier}' on device '{target_device}'")
                model_instance = loader_fn(weights_path_str, target_device)
                self._cache[cache_key] = model_instance
                return model_instance
            except Exception as exc:
                # Catch CUDA Out-of-Memory and attempt CPU fallback
                is_oom = "out of memory" in str(exc).lower() or "cuda" in str(exc).lower()
                if target_device == "cuda" and is_oom:
                    logger.warning(
                        f"CUDA allocation failed for '{identifier}' ({exc}). "
                        "Triggering OOM fallback to CPU."
                    )
                    try:
                        import torch  # type: ignore[import-not-found]

                        torch.cuda.empty_cache()
                    except Exception:
                        pass

                    cpu_key = f"{identifier}:cpu"
                    model_instance = loader_fn(weights_path_str, "cpu")
                    self._cache[cpu_key] = model_instance
                    return model_instance
                raise

    def clear_cache(self) -> None:
        """Clears cached model instances and releases PyTorch GPU memory if available."""
        with self._lock:
            self._cache.clear()
            try:
                import torch  # type: ignore[import-not-found]

                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass


model_manager = ModelManager()
