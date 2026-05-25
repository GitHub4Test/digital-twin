"""
API routes for common apis for backend service
"""

import logging
from fastapi import APIRouter, HTTPException, status
from api_service.models import (
    HealthCheckResponse,
    MessageResponse,
    ErrorResponse,
)
from api_service.db.database import db

logger = logging.getLogger(__name__)

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
    logger.info("Health check endpoint called")
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
    logger.info("Liveness probe endpoint called")
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
    logger.info("Readiness probe endpoint called")
    try:
        if not db.health_check():
            logger.error("Database health check failed")
            raise Exception("Database not reachable")

        logger.info("Service is ready to accept traffic")
        return HealthCheckResponse(
            status="ready",
            service="backend",
            version="1.0.0"
        )

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service not ready: {str(e)}"
        )