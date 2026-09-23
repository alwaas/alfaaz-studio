"""Test file storage service, path traversal security, and MIME validation."""

from pathlib import Path

import pytest

from app.core.exceptions import InvalidFileTypeException, StorageSecurityException
from app.core.security import (
    ALLOWED_AUDIO_MIMES,
    detect_mime_from_header,
    validate_mime_type,
    validate_safe_path,
)
from app.services.storage import storage_service


def test_mime_detection_from_headers() -> None:
    """Test magic bytes recognition for WAV, MP3, and MP4."""
    # Synthetic WAV header
    wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00"
    assert detect_mime_from_header(wav_header) == "audio/wav"

    # Synthetic MP3 ID3 header
    mp3_header = b"ID3\x03\x00\x00\x00\x00\x00\x00"
    assert detect_mime_from_header(mp3_header) == "audio/mpeg"

    # Synthetic MP4 ftyp header
    mp4_header = b"\x00\x00\x00\x18ftypmp42"
    assert detect_mime_from_header(mp4_header) == "video/mp4"

    # Unrecognized
    assert detect_mime_from_header(b"PLAIN_TEXT") is None


def test_mime_validation_rules() -> None:
    """Test valid and invalid MIME checks."""
    wav_header = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00"
    detected = validate_mime_type(wav_header, "voice.wav", ALLOWED_AUDIO_MIMES)
    assert detected == "audio/wav"

    # Executable payload disguised as .exe or .sh
    with pytest.raises(InvalidFileTypeException):
        validate_mime_type(b"MZ\x90\x00executable", "malware.exe", ALLOWED_AUDIO_MIMES)


def test_path_traversal_protection(tmp_path: Path) -> None:
    """Verify that path traversal attempts raise StorageSecurityException."""
    base_dir = tmp_path / "safe_storage"
    base_dir.mkdir()

    # Safe subpath
    safe = validate_safe_path(base_dir, "valid_file.wav")
    assert safe.parent == base_dir.resolve()

    # Traversal attack attempts
    with pytest.raises(StorageSecurityException):
        validate_safe_path(base_dir, "../outside.txt")

    with pytest.raises(StorageSecurityException):
        validate_safe_path(base_dir, "../../windows/system32/cmd.exe")

    with pytest.raises(StorageSecurityException):
        validate_safe_path(base_dir, "foo/../../bar")


@pytest.mark.asyncio
async def test_storage_service_save_and_delete() -> None:
    """Test saving a file through storage_service and deleting it."""
    wav_content = b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00" + (b"\x00" * 100)
    file_id, safe_path, size, mime = await storage_service.save_file(
        content=wav_content,
        filename="test_audio.wav",
        category="temp",
        allowed_mimes=ALLOWED_AUDIO_MIMES,
    )

    assert safe_path.exists()
    assert size == len(wav_content)
    assert mime == "audio/wav"

    # Fetch file path
    retrieved_path = storage_service.get_file_path(safe_path.name, category="temp")
    assert retrieved_path == safe_path

    # Delete file
    deleted = storage_service.delete_file(safe_path.name, category="temp")
    assert deleted is True
    assert not safe_path.exists()


def test_storage_stats_computation() -> None:
    """Test calculating storage stats for all categories."""
    stats = storage_service.get_storage_stats()
    assert "models" in stats
    assert "outputs" in stats
    assert "temp" in stats
    assert stats["temp"]["exists"] is True
