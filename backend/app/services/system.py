"""System telemetry, diagnostics, and hardware detection service."""

from typing import Any

import psutil  # type: ignore[import-untyped]
from sqlalchemy import text

from app.config import settings
from app.core.logging import get_logger
from app.db.session import engine

logger = get_logger(__name__)


class SystemService:
    """Service providing hardware telemetry, model inventories, and readiness probes."""

    @staticmethod
    def get_device_info() -> dict[str, Any]:
        """Detect compute device, CUDA availability, CPU cores, and RAM."""
        cuda_available = False
        cuda_count = 0
        device_name = None
        vram_total = None
        vram_used = None

        # Attempt to probe PyTorch if available in environment
        try:
            import torch  # type: ignore[import-not-found,import-untyped]

            cuda_available = torch.cuda.is_available()
            if cuda_available:
                cuda_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0)
                # VRAM in MB
                vram_total = round(
                    torch.cuda.get_device_properties(0).total_memory / (1024 * 1024), 2
                )
                vram_used = round(torch.cuda.memory_allocated(0) / (1024 * 1024), 2)
        except ImportError:
            logger.debug("PyTorch not loaded; reporting CPU hardware via psutil")

        effective_device = "cuda" if cuda_available and settings.DEVICE != "cpu" else "cpu"

        # System memory & CPU stats via psutil
        mem = psutil.virtual_memory()
        cpu_logical = psutil.cpu_count(logical=True) or 1
        cpu_physical = psutil.cpu_count(logical=False)
        cpu_usage = psutil.cpu_percent(interval=None)

        return {
            "configured_device": settings.DEVICE,
            "effective_device": effective_device,
            "cuda_available": cuda_available,
            "cuda_device_count": cuda_count,
            "cuda_device_name": device_name,
            "cuda_vram_total_mb": vram_total,
            "cuda_vram_used_mb": vram_used,
            "cpu_cores_logical": cpu_logical,
            "cpu_cores_physical": cpu_physical,
            "cpu_usage_percent": cpu_usage,
            "system_memory_total_mb": round(mem.total / (1024 * 1024), 2),
            "system_memory_available_mb": round(mem.available / (1024 * 1024), 2),
            "system_memory_used_percent": mem.percent,
        }

    @staticmethod
    def get_model_status() -> dict[str, Any]:
        """Inventory installed and known models in the models directory."""
        model_dir = settings.resolved_model_dir
        known_models = [
            {
                "name": "F5-TTS (Urdu DiT)",
                "engine": "f5-tts",
                "rel_path": "f5-tts-urdu",
                "license_type": "CC-BY-NC 4.0 / Research (Personal Use Only)",
            },
            {
                "name": "MeloTTS (Urdu VITS)",
                "engine": "melotts",
                "rel_path": "melotts-urdu",
                "license_type": "MIT License (Commercial & Personal)",
            },
            {
                "name": "Piper TTS (Urdu ONNX)",
                "engine": "piper",
                "rel_path": "piper-urdu",
                "license_type": "MIT / GPL (Commercial & Personal)",
            },
            {
                "name": "Whisper Timestamp Aligner",
                "engine": "whisper",
                "rel_path": "whisper-base",
                "license_type": "MIT License",
            },
        ]

        models_list = []
        installed_count = 0

        for item in known_models:
            full_path = model_dir / item["rel_path"]
            installed = full_path.exists()
            size_mb = None
            if installed:
                installed_count += 1
                if full_path.is_file():
                    size_mb = round(full_path.stat().st_size / (1024 * 1024), 2)
                elif full_path.is_dir():
                    total_bytes = sum(
                        f.stat().st_size for f in full_path.glob("**/*") if f.is_file()
                    )
                    size_mb = round(total_bytes / (1024 * 1024), 2)

            models_list.append(
                {
                    "name": item["name"],
                    "engine": item["engine"],
                    "path": str(full_path),
                    "installed": installed,
                    "size_mb": size_mb,
                    "license_type": item["license_type"],
                }
            )

        return {
            "default_engine": settings.DEFAULT_TTS_ENGINE,
            "fallback_engine": settings.FALLBACK_TTS_ENGINE,
            "models_directory": str(model_dir),
            "installed_count": installed_count,
            "models": models_list,
        }

    @staticmethod
    async def check_readiness() -> dict[str, Any]:
        """Perform comprehensive readiness probe across database and storage."""
        checks: dict[str, bool] = {
            "database": False,
            "model_storage": False,
            "output_storage": False,
            "temp_storage": False,
        }
        details: dict[str, Any] = {}

        # 1. Database check
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["database"] = True
            details["database"] = "Connected successfully"
        except Exception as exc:
            checks["database"] = False
            details["database"] = f"Connection failed: {exc}"

        # 2. Storage write/read checks
        for key, dir_path in [
            ("model_storage", settings.resolved_model_dir),
            ("output_storage", settings.resolved_output_dir),
            ("temp_storage", settings.resolved_temp_dir),
        ]:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                test_file = dir_path / ".probe_check"
                test_file.write_text("probe_ok", encoding="utf-8")
                test_file.unlink()
                checks[key] = True
                details[key] = "Writable and readable"
            except Exception as exc:
                checks[key] = False
                details[key] = f"Access check failed: {exc}"

        all_ready = all(checks.values())
        return {
            "ready": all_ready,
            "checks": checks,
            "details": details,
        }


system_service = SystemService()
