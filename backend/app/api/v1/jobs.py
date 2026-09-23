"""Job tracking and status endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Job
from app.db.session import get_db
from app.schemas.job import JobLogsResponse, JobResponse
from app.services.queue import get_job_logs, mark_job_cancelled

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get job status",
    description="Poll progress percentage and execution status for an async job.",
)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Retrieve state, progress, and result payload of an asynchronous job."""
    query = select(Job).where(Job.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id '{job_id}' not found",
        )

    return JobResponse.model_validate(job)


@router.post(
    "/{job_id}/cancel",
    response_model=JobResponse,
    summary="Cancel active job",
    description="Signal an in-flight job to abort execution.",
)
async def cancel_job(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> JobResponse:
    """Request cooperative cancellation of a background job."""
    query = select(Job).where(Job.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id '{job_id}' not found",
        )

    if job.status in ("completed", "failed", "cancelled"):
        return JobResponse.model_validate(job)

    # Flag cancellation in queue and update DB
    mark_job_cancelled(job_id)
    job.status = "cancelled"
    await db.commit()
    await db.refresh(job)

    return JobResponse.model_validate(job)


@router.get(
    "/{job_id}/logs",
    response_model=JobLogsResponse,
    summary="Get job execution logs",
    description="Retrieve live event log lines for a background processing job.",
)
async def get_job_execution_logs(
    job_id: str,
    db: AsyncSession = Depends(get_db),
) -> JobLogsResponse:
    """Retrieve event logs for a specific job."""
    query = select(Job).where(Job.id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id '{job_id}' not found",
        )

    logs = get_job_logs(job_id)
    return JobLogsResponse(job_id=job_id, status=job.status, logs=logs)
