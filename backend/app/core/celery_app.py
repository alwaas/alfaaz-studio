"""Celery application and worker configuration."""

from celery import Celery  # type: ignore[import-untyped]
from app.config import settings

# Initialize Celery app
celery_app = Celery(
    "alfaaz_studio",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Apply configuration
celery_app.conf.update(
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=True,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,
    result_expires=3600,
)
