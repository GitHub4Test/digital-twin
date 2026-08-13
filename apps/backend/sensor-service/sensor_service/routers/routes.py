"""
API routes for health checks of sensor service
"""

import logging

from fastapi import APIRouter, HTTPException, Response, status

from sensor_service.db_controller.db_mgr import db_mgr
from sensor_service.rabbitmq_controller.rabbitmq_mgr import rabbitmq

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["health-checks"])

from fastapi import FastAPI

api = FastAPI()


@api.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}


# Health check endpoint
@router.get(
    "/health",
    summary="Health check",
    description="Returns the health status of the backend service.",
)
async def api_health():
    logger.debug("Health check endpoint API")

    return {"status": "healthy"}


# Liveness probe
@router.get(
    "/live",
    summary="Liveness probe",
    description="Checks if the service is accessible.",
)
async def api_liveness():
    logger.info("Liveness probe endpoint called")
    return {"status": "live"}


# Readiness probe
@router.get(
    "/ready",
    summary="Readiness probe",
    description="Checks if the service is ready to accept the requests.",
)
async def api_readiness(response: Response):
    logger.info("Readiness probe endpoint called")
    try:
        if not db_mgr.health_check():
            logger.error("Database health check failed")
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {
                "status": "not_ready",
                "database": "disconnected",
            }

        if not rabbitmq.is_connected():
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            logger.error("RabbitMQ health check failed")
            return {
                "status": "not_ready",
                "rabbitmq": "disconnected",
            }

        logger.info("Service is ready to accept traffic")
        return {"status": "ready"}

    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        logger.error(f"Readiness check failed: {e!s}")
        raise HTTPException(
            status_code=503, detail=f"Service not ready: {e!s}"
        )
