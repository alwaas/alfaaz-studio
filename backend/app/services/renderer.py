"""FFmpeg 9:16 Vertical Reel Video Rendering Service.

Combines background video/canvas loops, mastered audio tracks, and
burned-in ASS Nastaliq subtitles into cinematic 1080x1920 Instagram Reels.
"""

import asyncio
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.exceptions import AudioProcessingError
from app.services.subtitles import ASSSubtitleBuilder, SubtitleVerse


@dataclass
class ReelTheme:
    """Aesthetic visual theme preset for poetry reels."""

    id: str
    name: str
    description: str
    bg_color_hex: str
    accent_color_hex: str
    font_color_hex: str
    vignette_intensity: float = 0.4


REEL_THEMES: dict[str, ReelTheme] = {
    "velvet-gold": ReelTheme(
        id="velvet-gold",
        name="Velvet & Gold (شاہانہ مخمل و زر)",
        description="Deep midnight navy (#080B14) with royal gold calligraphy accents",
        bg_color_hex="0x080B14",
        accent_color_hex="0xF59E0B",
        font_color_hex="0xFFFFFF",
        vignette_intensity=0.5,
    ),
    "emerald-night": ReelTheme(
        id="emerald-night",
        name="Mughal Emerald (مغلیہ زمرد)",
        description="Rich atmospheric jade-emerald (#06140E) for soulful classic ghazals",
        bg_color_hex="0x06140E",
        accent_color_hex="0x10B981",
        font_color_hex="0xF8FAFC",
        vignette_intensity=0.45,
    ),
    "candlelight": ReelTheme(
        id="candlelight",
        name="Candlelit Amber (شمع و محفل)",
        description="Warm incandescent sepia and dark charcoal (#140B07) for romantic verses",
        bg_color_hex="0x140B07",
        accent_color_hex="0xFB923C",
        font_color_hex="0xFFFBEB",
        vignette_intensity=0.55,
    ),
    "monochrome-rain": ReelTheme(
        id="monochrome-rain",
        name="Noir Rain (سیاہ و سفید بارش)",
        description="Moody high-contrast slate (#0A0C10) for melancholic modern couplets",
        bg_color_hex="0x0A0C10",
        accent_color_hex="0x94A3B8",
        font_color_hex="0xF1F5F9",
        vignette_intensity=0.6,
    ),
}


def escape_ffmpeg_path(path: Path | str) -> str:
    """Escapes path string for FFmpeg filter expressions on Windows and Unix."""
    raw = str(path).replace("\\", "/")
    # Windows drive letter colon (e.g., C:/ -> C\:/)
    escaped = raw.replace(":", r"\:")
    # Single quotes in path
    escaped = escaped.replace("'", r"\'")
    return escaped


class ReelRenderer:
    """Async FFmpeg video render pipeline for 9:16 vertical reels."""

    def __init__(self, ffmpeg_bin: str = "ffmpeg") -> None:
        self.ffmpeg_bin = ffmpeg_bin

    def is_ffmpeg_available(self) -> bool:
        """Verifies if FFmpeg binary is available on PATH."""
        return shutil.which(self.ffmpeg_bin) is not None

    async def get_ffmpeg_version(self) -> str:
        """Retrieves installed FFmpeg version string."""
        if not self.is_ffmpeg_available():
            return "FFmpeg not found"
        try:
            proc = await asyncio.create_subprocess_exec(
                self.ffmpeg_bin,
                "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            first_line = stdout.decode("utf-8", errors="ignore").splitlines()[0]
            return first_line
        except Exception as exc:
            return f"Error detecting FFmpeg: {exc}"

    def build_render_command(
        self,
        audio_path: Path,
        ass_path: Path,
        output_path: Path,
        duration: float,
        bg_video_path: Path | None = None,
        theme: ReelTheme | None = None,
        fps: int = 30,
        resolution: tuple[int, int] = (1080, 1920),
    ) -> list[str]:
        """Constructs FFmpeg CLI arguments list for 9:16 reel rendering."""
        selected_theme = theme or REEL_THEMES["velvet-gold"]
        width, height = resolution
        escaped_ass = escape_ffmpeg_path(ass_path)

        cmd: list[str] = [self.ffmpeg_bin, "-y"]

        if bg_video_path and bg_video_path.exists():
            # Loop background video to match audio length
            cmd.extend([
                "-stream_loop", "-1",
                "-i", str(bg_video_path),
                "-i", str(audio_path),
            ])
            # Scale & crop to 9:16 + burn subtitles
            filter_chain = (
                f"scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height},setsar=1,"
                f"ass='{escaped_ass}'"
            )
        else:
            # Procedural elegant atmospheric canvas with vignette
            bg_color = selected_theme.bg_color_hex
            cmd.extend([
                "-f", "lavfi",
                "-i", f"color=c={bg_color}:s={width}x{height}:d={duration:.2f}:r={fps}",
                "-i", str(audio_path),
            ])
            vignette = f"vignette=PI/4*{selected_theme.vignette_intensity:.2f}"
            filter_chain = f"{vignette},ass='{escaped_ass}'"

        cmd.extend([
            "-filter_complex", f"[0:v]{filter_chain}[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "21",
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-t", f"{duration:.3f}",
            "-movflags", "+faststart",
            str(output_path),
        ])

        return cmd

    async def render_reel(
        self,
        audio_path: Path,
        verses: list[SubtitleVerse],
        output_path: Path,
        duration: float,
        title: str | None = None,
        poet_name: str | None = None,
        bg_video_path: Path | None = None,
        theme_id: str = "velvet-gold",
        font_name: str = "Noto Nastaliq Urdu",
        font_size: int = 60,
        enable_karaoke: bool = True,
        fps: int = 30,
    ) -> Path:
        """Executes full end-to-end rendering of a 9:16 vertical MP4 reel."""
        if not self.is_ffmpeg_available():
            raise AudioProcessingError("FFmpeg executable not found on system PATH.")

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio track not found at: {audio_path}")

        theme = REEL_THEMES.get(theme_id, REEL_THEMES["velvet-gold"])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Generate ASS Subtitle File
        sub_builder = ASSSubtitleBuilder(
            font_name=font_name,
            font_size=font_size,
            resolution_x=1080,
            resolution_y=1920,
        )

        with tempfile.NamedTemporaryFile(suffix=".ass", delete=False) as tmp_ass:
            ass_path = Path(tmp_ass.name)

        try:
            sub_builder.write_ass_file(
                output_path=ass_path,
                verses=verses,
                title=title,
                poet_name=poet_name,
                enable_karaoke=enable_karaoke,
            )

            # 2. Build FFmpeg command
            cmd = self.build_render_command(
                audio_path=audio_path,
                ass_path=ass_path,
                output_path=output_path,
                duration=duration,
                bg_video_path=bg_video_path,
                theme=theme,
                fps=fps,
            )

            # 3. Execute render process
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                err_msg = stderr.decode("utf-8", errors="ignore")
                # Fallback check: if 'ass' filter failed due to font or filter library, retry with simpler color
                raise AudioProcessingError(f"FFmpeg render failed (code {proc.returncode}): {err_msg[-400:]}")

            return output_path
        finally:
            if ass_path.exists():
                ass_path.unlink(missing_ok=True)


# Singleton renderer instance
reel_renderer = ReelRenderer()

