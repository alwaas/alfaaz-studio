"""Custom exceptions and error responses for AlfaazStudio."""

from typing import Any


class AlfaazStudioException(Exception):
    """Base exception class for AlfaazStudio."""

    def __init__(self, message: str, details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details


class ResourceNotFoundException(AlfaazStudioException):
    """Exception raised when a requested resource does not exist."""

    pass


class StorageSecurityException(AlfaazStudioException):
    """Exception raised on path traversal or file permission violations."""

    pass


class InvalidFileTypeException(AlfaazStudioException):
    """Exception raised when an uploaded file violates MIME type constraints."""

    pass


class HardwareUnavailableException(AlfaazStudioException):
    """Exception raised when requested compute hardware is unreachable."""

    pass


class AudioProcessingError(AlfaazStudioException):
    """Exception raised during audio manipulation, DSP processing, or TTS synthesis."""

    pass


class ModelInferenceError(AlfaazStudioException):
    """Exception raised during neural speech model execution."""

    pass
