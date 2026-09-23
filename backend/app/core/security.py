"""Security and validation utilities."""

import os
from pathlib import Path

from app.core.exceptions import InvalidFileTypeException, StorageSecurityException

ALLOWED_AUDIO_MIMES: set[str] = {
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/mpeg",
    "audio/mp3",
    "audio/ogg",
    "audio/flac",
    "audio/x-m4a",
}

ALLOWED_VIDEO_MIMES: set[str] = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}

ALLOWED_IMAGE_MIMES: set[str] = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

ALLOWED_EXTENSIONS_MAP: dict[str, str] = {
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".flac": "audio/flac",
    ".m4a": "audio/x-m4a",
    ".mp4": "video/mp4",
    ".mov": "video/quicktime",
    ".webm": "video/webm",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
    ".ass": "text/x-ass",
}


def validate_safe_path(base_directory: Path, target_path: str | Path) -> Path:
    """
    Validate that target_path resolves strictly within base_directory.
    Protects against directory traversal attacks (e.g. '../', absolute paths).
    """
    base_resolved = base_directory.resolve()

    # Check for null bytes in string
    if isinstance(target_path, str) and "\0" in target_path:
        raise StorageSecurityException("Path contains invalid null byte character")

    target_candidate = (base_resolved / target_path).resolve()

    try:
        # relative_to will raise ValueError if target_candidate is not within base_resolved
        target_candidate.relative_to(base_resolved)
    except ValueError as err:
        raise StorageSecurityException(
            f"Path traversal detected: '{target_path}' escapes base directory '{base_directory}'"
        ) from err

    return target_candidate


def detect_mime_from_header(data: bytes) -> str | None:
    """Examine file magic bytes to determine actual MIME type."""
    if len(data) < 4:
        return None

    # WAV: 'RIFF....WAVE'
    if data[:4] == b"RIFF" and len(data) >= 12 and data[8:12] == b"WAVE":
        return "audio/wav"
    # MP3: ID3 or frame sync 0xFFFB/0xFFFA
    if data[:3] == b"ID3" or (data[0] == 0xFF and (data[1] & 0xE0) == 0xE0):
        return "audio/mpeg"
    # OGG
    if data[:4] == b"OggS":
        return "audio/ogg"
    # FLAC
    if data[:4] == b"fLaC":
        return "audio/flac"
    # PNG: \x89PNG\r\n\x1a\n
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    # JPEG: \xff\xd8\xff
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    # WEBP: 'RIFF....WEBP'
    if data[:4] == b"RIFF" and len(data) >= 12 and data[8:12] == b"WEBP":
        return "image/webp"
    # MP4: ....ftyp
    if len(data) >= 8 and data[4:8] == b"ftyp":
        return "video/mp4"

    return None


def validate_mime_type(content: bytes, filename: str, allowed_types: set[str]) -> str:
    """
    Validate file MIME type using both magic header detection and extension matching.
    """
    detected_mime = detect_mime_from_header(content)
    ext = os.path.splitext(filename)[1].lower()
    ext_mime = ALLOWED_EXTENSIONS_MAP.get(ext)

    # Determine effective mime
    effective_mime = detected_mime or ext_mime

    if not effective_mime or effective_mime not in allowed_types:
        raise InvalidFileTypeException(
            f"File '{filename}' of type '{effective_mime or 'unknown'}' is not permitted. Allowed: {sorted(allowed_types)}"
        )

    return effective_mime
