"""
API routes for sensor data management
"""

from fastapi import APIRouter, HTTPException, Query, status
from src.models import (
    SensorReadingCreate,
    SensorReadingResponse,
    HealthCheckResponse,
    MessageResponse,
    ErrorResponse,
)
from src.database import Database

router = APIRouter(
    prefix="/api/v1",
    tags=["sensor-data"]
)
db = Database()


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

@router.post(
    "/readings",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create sensor reading",
    description="Insert a new sensor reading into the database.",
    responses={
        201: {"description": "Sensor reading stored successfully"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def create_sensor_reading(reading: SensorReadingCreate):
    try:
        db.insert_reading(
            reading.timestamp,
            reading.temperature,
            reading.humidity
        )
        return MessageResponse(message="Sensor reading stored successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/readings",
    response_model=list[SensorReadingResponse],
    summary="List sensor readings",
    description="Retrieve the most recent sensor readings ordered by timestamp descending.",
    responses={
        200: {"description": "List of sensor readings"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def get_sensor_data(
    limit: int = Query(
        200,
        ge=1,
        le=1000,
        description="Maximum number of sensor readings to return"
    )
):
    try:
        readings = db.get_readings(limit)
        return readings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete(
    "/readings",
    response_model=MessageResponse,
    summary="Delete all sensor readings",
    description="Remove all sensor readings from the database.",
    responses={
        200: {"description": "All sensor readings deleted"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def clear_sensor_data():
    try:
        db.clear_readings()
        return MessageResponse(message="All sensor readings cleared successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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