"""
API routes for health checks of backend services
"""

import logging
import requests
from fastapi import APIRouter, HTTPException, status
from api_gateway.models import (
    HealthCheckResponse,
    MessageResponse,
    ErrorResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["health-checks"]
)

# Health check endpoint
@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Returns the health status of the backend service."
)
async def api_health():
    logger.debug("Health check endpoint API")
    
    return HealthCheckResponse(
        status="healthy",
        service="backend",
        version="1.0.0"
    )

# Liveness probe
@router.get(
    "/live",
    response_model=HealthCheckResponse,
    summary="Liveness probe",
    description="Checks if the service is accessible."
)
async def api_liveness():
    logger.info("Liveness probe endpoint called")
    return HealthCheckResponse(
        status="alive",
        service="backend",
        version="1.0.0"
    )

# Readiness probe
@router.get(
    "/ready",
    response_model=HealthCheckResponse,
    summary="Readiness probe",
    description="Checks if the service is ready to accept the requests."
)
async def api_readiness():
    logger.info("Readiness probe endpoint called")
    try:
        # if not db.health_check():
        #     logger.error("Database health check failed")
        #     raise Exception("Database not reachable")

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