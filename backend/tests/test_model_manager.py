"""Unit tests for ModelManager and HardwareManager."""

import tempfile
from pathlib import Path

from app.services.tts.model_manager import (
    HardwareManager,
    ModelManager,
)


def test_hardware_detection() -> None:
    """Verifies hardware device detection and precision selection."""
    device = HardwareManager.detect_device()
    assert device in ("cuda", "cpu")

    info = HardwareManager.get_device_info()
    assert "device" in info
    assert "cpu_count" in info
    assert "ram_total_mb" in info
    assert info["cpu_count"] >= 1

    precision_cuda = HardwareManager.get_precision("cuda")
    assert precision_cuda in ("bfloat16", "float16")
    precision_cpu = HardwareManager.get_precision("cpu")
    assert precision_cpu == "float32"


def test_model_metadata_registry() -> None:
    """Verifies default registered models and license tracking."""
    mm = ModelManager()
    f5_meta = mm.get_metadata("f5-tts-urdu")
    assert f5_meta is not None
    assert f5_meta.engine == "f5-tts"
    assert f5_meta.license_type == "CC-BY-NC-4.0"
    assert f5_meta.commercial_allowed is False  # Non-commercial personal use only
    assert f5_meta.expected_sample_rate == 24000

    melo_meta = mm.get_metadata("melotts")
    assert melo_meta is not None
    assert melo_meta.license_type == "MIT"
    assert melo_meta.commercial_allowed is True
    assert melo_meta.expected_sample_rate == 22050

    piper_meta = mm.get_metadata("piper")
    assert piper_meta is not None
    assert piper_meta.license_type == "MIT"
    assert piper_meta.commercial_allowed is True

    all_models = mm.list_models()
    assert len(all_models) >= 3


def test_checksum_verification() -> None:
    """Verifies SHA-256 calculation and checksum matching."""
    mm = ModelManager()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
        tmp.write(b"AlfaazStudio Model Weights Verification Sample 12345")
        tmp_path = Path(tmp.name)

    try:
        real_hash = mm.compute_sha256(tmp_path)
        assert len(real_hash) == 64
        # Verify matching
        assert mm.verify_checksum(tmp_path, real_hash) is True
        # Verify mismatch
        assert mm.verify_checksum(tmp_path, "0" * 64) is False
        # Non-existent file
        assert mm.verify_checksum(Path("non_existent_file.safetensors"), real_hash) is False
    finally:
        tmp_path.unlink(missing_ok=True)


def test_model_cache_and_oom_recovery() -> None:
    """Verifies model caching and CPU failover on CUDA OOM."""
    mm = ModelManager()

    call_count = 0

    def mock_loader(weights_path: str, device: str) -> dict[str, str]:
        nonlocal call_count
        call_count += 1
        return {"loaded_on": device, "weights": weights_path}

    # First load
    m1 = mm.get_or_load_model("piper", mock_loader, device="cpu")
    assert m1["loaded_on"] == "cpu"
    assert call_count == 1

    # Second load from cache
    m2 = mm.get_or_load_model("piper", mock_loader, device="cpu")
    assert m2 is m1
    assert call_count == 1

    # OOM recovery simulation
    def oom_loader(weights_path: str, device: str) -> dict[str, str]:
        if device == "cuda":
            raise RuntimeError("CUDA out of memory. Tried to allocate 2.00 GiB")
        return {"loaded_on": "cpu_fallback"}

    fallback_model = mm.get_or_load_model("f5-tts-urdu", oom_loader, device="cuda")
    assert fallback_model["loaded_on"] == "cpu_fallback"

    # Test cache clearing
    mm.clear_cache()
    assert len(mm._cache) == 0

