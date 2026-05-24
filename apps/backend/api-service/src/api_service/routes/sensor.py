"""
API routes for sensor data management
"""

from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Query, Header
from api_service.models import (
    SensorReadingCreate,
    SensorReadingResponse,
    HealthCheckResponse,
    MessageResponse,
    ErrorResponse,
)

from api_service.rabbitmq.events import SensorReadingEvent
from api_service.rabbitmq.publisher import publish_sensor_event
from api_service.routes.common import db
from api_service.resilience import publish_with_resilience

router = APIRouter(prefix="/api/v1", tags=["sensor-data"])


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
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

@router.post(
    "/readings/event",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Accept sensor reading",
    description="Accept a sensor reading and enqueue it for asynchronous processing."
)
async def create_sensor_reading_event(
    reading: SensorReadingCreate,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")
):
    print("Inside create_sensor_reading_event")
    
    try:
        event = SensorReadingEvent(
            event_id=idempotency_key or str(uuid4()),
            timestamp=reading.timestamp,
            temperature=reading.temperature,
            humidity=reading.humidity,
        )

        await publish_with_resilience(
            publish_sensor_event,
            event.model_dump(mode="json")
        )

        return MessageResponse(
            message="Sensor reading accepted for processing"
        )

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RabbitMQ unavailable: {str(e)}")
        
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
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")

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
