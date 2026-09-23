"""File storage service for managing audio, video, models, and temp assets."""

import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Any

from app.config import settings
from app.core.exceptions import StorageSecurityException
from app.core.logging import get_logger
from app.core.security import (
    validate_mime_type,
    validate_safe_path,
)

logger = get_logger(__name__)


class StorageService:
    """Service providing safe, sandboxed file operations with path traversal protection."""

    def __init__(self) -> None:
        self.model_dir = settings.resolved_model_dir
        self.output_dir = settings.resolved_output_dir
        self.temp_dir = settings.resolved_temp_dir

        # Ensure base directories exist
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def _get_category_dir(self, category: str) -> Path:
        """Resolve directory path by category name."""
        match category:
            case "models":
                return self.model_dir
            case "outputs":
                return self.output_dir
            case "temp":
                return self.temp_dir
            case _:
                raise StorageSecurityException(f"Invalid storage category: '{category}'")

    async def save_file(
        self,
        content: bytes,
        filename: str,
        category: str = "temp",
        allowed_mimes: set[str] | None = None,
    ) -> tuple[str, Path, int, str]:
        """
        Validate, sandbox, and save binary content to disk.
        Returns: (file_id, safe_path, size_in_bytes, mime_type)
        """
        base_dir = self._get_category_dir(category)

        # Sanitize filename extension
        ext = os.path.splitext(filename)[1].lower()
        file_id = str(uuid.uuid4())
        safe_filename = f"{file_id}{ext}"

        # Validate path to ensure no traversal
        target_path = validate_safe_path(base_dir, safe_filename)

        # Validate MIME type if restrictions are specified
        mime_type = "application/octet-stream"
        if allowed_mimes is not None:
            mime_type = validate_mime_type(content, filename, allowed_mimes)

        # Write to disk
        target_path.write_bytes(content)
        size = len(content)

        logger.info(f"Saved file '{safe_filename}' ({size} bytes, {mime_type}) in '{category}'")
        return file_id, target_path, size, mime_type

    def get_file_path(self, filename: str, category: str = "temp") -> Path:
        """Retrieve and validate safe path for a file."""
        base_dir = self._get_category_dir(category)
        safe_path = validate_safe_path(base_dir, filename)
        if not safe_path.exists():
            raise FileNotFoundError(f"File '{filename}' not found in category '{category}'")
        return safe_path

    def delete_file(self, filename: str, category: str = "temp") -> bool:
        """Safely delete a file if it exists."""
        base_dir = self._get_category_dir(category)
        safe_path = validate_safe_path(base_dir, filename)
        if safe_path.exists() and safe_path.is_file():
            safe_path.unlink()
            logger.info(f"Deleted file '{safe_path.name}' from '{category}'")
            return True
        return False

    def cleanup_temp_files(self, max_age_hours: int = 24) -> int:
        """Remove temporary files older than max_age_hours."""
        now = time.time()
        cutoff = now - (max_age_hours * 3600)
        deleted_count = 0

        for item in self.temp_dir.iterdir():
            if item.is_file() and item.name != ".gitkeep":
                try:
                    if item.stat().st_mtime < cutoff:
                        item.unlink()
                        deleted_count += 1
                except Exception as err:
                    logger.warning(f"Failed to delete temp file {item}: {err}")

        logger.info(f"Cleaned up {deleted_count} stale temporary files")
        return deleted_count

    def get_storage_stats(self) -> dict[str, dict[str, Any]]:
        """Calculate disk usage stats across storage categories."""
        stats = {}
        for category, path in [
            ("models", self.model_dir),
            ("outputs", self.output_dir),
            ("temp", self.temp_dir),
        ]:
            if path.exists():
                try:
                    usage = shutil.disk_usage(str(path))
                    percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0.0
                    stats[category] = {
                        "path": str(path),
                        "exists": True,
                        "total_bytes": usage.total,
                        "used_bytes": usage.used,
                        "free_bytes": usage.free,
                        "percent_used": round(percent, 2),
                    }
                except Exception:
                    stats[category] = {
                        "path": str(path),
                        "exists": True,
                        "total_bytes": 0,
                        "used_bytes": 0,
                        "free_bytes": 0,
                        "percent_used": 0.0,
                    }
            else:
                stats[category] = {
                    "path": str(path),
                    "exists": False,
                    "total_bytes": 0,
                    "used_bytes": 0,
                    "free_bytes": 0,
                    "percent_used": 0.0,
                }
        return stats


storage_service = StorageService()
