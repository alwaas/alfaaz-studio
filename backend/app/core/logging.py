"""Structured logging configuration for AlfaazStudio."""

import logging
import sys
from contextvars import ContextVar

# Request correlation ID context variable
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class StructuredFormatter(logging.Formatter):
    """Custom formatter that adds correlation ID to log records."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_ctx.get()
        record.request_id = req_id if req_id else "-"
        return super().format(record)


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger with structured formatting."""
    log_format = "[%(asctime)s] [%(levelname)s] [%(name)s] [req:%(request_id)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    formatter = StructuredFormatter(fmt=log_format, datefmt=date_format)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers to prevent duplicate lines
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name."""
    return logging.getLogger(name)
