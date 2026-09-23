"""Unit tests for FFmpeg 9:16 Reel Video Renderer service."""

import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf  # type: ignore[import-untyped]

from app.services.renderer import (
    REEL_THEMES,
    escape_ffmpeg_path,
    reel_renderer,
)
from app.services.subtitles import SubtitleVerse


def test_reel_themes_registry() -> None:
    """Verifies predefined aesthetic themes for 9:16 reels."""
    assert len(REEL_THEMES) >= 4
    assert "velvet-gold" in REEL_THEMES
    assert "emerald-night" in REEL_THEMES
    assert "candlelight" in REEL_THEMES
    assert "monochrome-rain" in REEL_THEMES

    theme = REEL_THEMES["velvet-gold"]
    assert theme.bg_color_hex.startswith("0x")
    assert len(theme.accent_color_hex) in (6, 7, 8)


def test_escape_ffmpeg_path() -> None:
    """Verifies that paths on Windows and Unix are correctly escaped for FFmpeg filters."""
    win_path = r"C:\Users\Alfaaz\temp\subtitles.ass"
    escaped = escape_ffmpeg_path(win_path)
    assert r"C\:/" in escaped
    assert "Users/Alfaaz/temp/subtitles.ass" in escaped


def test_build_render_command() -> None:
    """Verifies construction of FFmpeg CLI arguments."""
    audio = Path("temp/voice.wav")
    ass = Path("temp/subs.ass")
    out = Path("temp/output.mp4")

    cmd = reel_renderer.build_render_command(
        audio_path=audio,
        ass_path=ass,
        output_path=out,
        duration=5.0,
        fps=30,
        resolution=(1080, 1920),
    )

    cmd_str = " ".join(cmd)
    assert "1080x1920" in cmd_str
    assert "libx264" in cmd_str
    assert "aac" in cmd_str
    assert "-shortest" in cmd_str
    assert "-movflags +faststart" in cmd_str


@pytest.mark.asyncio
async def test_ffmpeg_version_check() -> None:
    """Verifies version detection of FFmpeg."""
    version = await reel_renderer.get_ffmpeg_version()
    assert "ffmpeg" in version.lower() or "version" in version.lower()


@pytest.mark.asyncio
async def test_render_reel_execution() -> None:
    """Verifies actual FFmpeg execution creating a 1080x1920 MP4 file."""
    if not reel_renderer.is_ffmpeg_available():
        pytest.skip("FFmpeg not installed")

    sr = 24000
    duration = 1.0
    samples = (0.2 * np.sin(2.0 * np.pi * 440.0 * np.linspace(0, duration, int(duration * sr), endpoint=False))).astype(np.float32)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
        sf.write(tmp_audio.name, samples, sr, subtype="PCM_16")
        audio_path = Path(tmp_audio.name)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_video:
        output_video_path = Path(tmp_video.name)

    verses = [
        SubtitleVerse(
            text="ٹیسٹ ریل ویڈیو",
            start_time=0.0,
            end_time=1.0,
        )
    ]

    try:
        rendered = await reel_renderer.render_reel(
            audio_path=audio_path,
            verses=verses,
            output_path=output_video_path,
            duration=duration,
            title="ٹیسٹ ریل",
            poet_name="شاعر",
            theme_id="velvet-gold",
            fps=15,  # Faster render for test
        )

        assert rendered.exists()
        assert rendered.stat().st_size > 1000
    finally:
        audio_path.unlink(missing_ok=True)
        output_video_path.unlink(missing_ok=True)
