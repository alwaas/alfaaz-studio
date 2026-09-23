"""API v1 master router."""

from fastapi import APIRouter

from app.api.v1.audio import router as audio_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.projects import router as projects_router
from app.api.v1.rendering import router as rendering_router
from app.api.v1.system import router as system_router
from app.api.v1.voices import router as voices_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(system_router)
api_v1_router.include_router(voices_router)
api_v1_router.include_router(projects_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(audio_router)
api_v1_router.include_router(rendering_router)
