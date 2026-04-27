"""
API routes for common apis for backend service
"""

from fastapi import APIRouter, HTTPException, status
from src.models import (
    HealthCheckResponse,
    MessageResponse,
    ErrorResponse,
)
from src.db.database import db

router = APIRouter(
    prefix="/api/v1",
    tags=["common"]
)

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Returns the health status of the backend service."
)
async def health_check():
    return HealthCheckResponse(
        status="healthy",
        service="backend",
        version="1.0.0"
    )

@router.get(
    "/live",
    response_model=HealthCheckResponse,
    summary="Liveness probe"
)
async def liveness_check():
    return HealthCheckResponse(
        status="alive",
        service="backend",
        version="1.0.0"
    )

@router.get(
    "/ready",
    response_model=HealthCheckResponse,
    summary="Readiness probe",
    description="Checks if the service is ready to accept traffic (DB connectivity)."
)
async def readiness_check():
    try:
        if not db.health_check():
            raise Exception("Database not reachable")

        return HealthCheckResponse(
            status="ready",
            service="backend",
            version="1.0.0"
        )

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )