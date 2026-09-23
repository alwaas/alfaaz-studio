"""Architecture and environment verification tests."""

from app.config import settings


def test_settings_initialization() -> None:
    """Verify that settings load with expected defaults."""
    assert settings.APP_NAME == "AlfaazStudio"
    assert settings.APP_VERSION == "0.1.0"
    assert settings.VIDEO_WIDTH == 1080
    assert settings.VIDEO_HEIGHT == 1920
    assert settings.SAMPLE_RATE == 24000


def test_required_directories_exist() -> None:
    """Verify that required project workspace directories exist."""
    base_dir = settings.BASE_DIR
    assert (base_dir / "backend").is_dir()
    assert (base_dir / "frontend").is_dir()
    assert (base_dir / "infra").is_dir()
    assert (base_dir / "models").is_dir()
    assert (base_dir / "outputs").is_dir()
    assert (base_dir / "temp").is_dir()


def test_required_documentation_files_exist() -> None:
    """Verify that critical legal and architecture documentation files exist."""
    base_dir = settings.BASE_DIR
    assert (base_dir / "MODEL_LICENSES.md").is_file()
    assert (base_dir / "ARCHITECTURE.md").is_file()
    assert (base_dir / "PRIVACY.md").is_file()
    assert (base_dir / "PROJECT_PLAN.md").is_file()
    assert (base_dir / ".env.example").is_file()


def test_model_licenses_content() -> None:
    """Verify MODEL_LICENSES.md contains mandatory legal declarations."""
    content = (settings.BASE_DIR / "MODEL_LICENSES.md").read_text(encoding="utf-8")
    assert "F5-TTS" in content
    assert "license" in content
    assert "personal use" in content


def test_architecture_content() -> None:
    """Verify ARCHITECTURE.md contains mandatory architectural elements."""
    content = (settings.BASE_DIR / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "diagram" in content
    assert "component" in content
    assert "FastAPI" in content
    assert "Next.js" in content
