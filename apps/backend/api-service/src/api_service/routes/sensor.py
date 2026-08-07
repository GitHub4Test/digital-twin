"""
API routes for sensor data management
"""

import logging
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
from api_service.routes.common import db
from api_service.db.exceptions import DuplicateEventError

logger = logging.getLogger(__name__)

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
    event_id = str(uuid4())
    try:
        logger.info(f"Creating sensor reading: temperature={reading.temperature}C, humidity={reading.humidity}%")
        db.insert_reading(
            event_id,
            reading.timestamp,
            reading.temperature,
            reading.humidity
        )
        logger.info(f"Sensor reading stored successfully: event_id={event_id}")
        return MessageResponse(message="Sensor reading stored successfully", event_id=event_id, status="RECEIVED")
    except Exception as e:
        logger.error(f"Failed to store sensor reading: {str(e)}")
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
    event_id = idempotency_key or str(uuid4())
    logger.info(f"Processing sensor reading event: event_id={event_id}")

    payload = SensorReadingEvent(
        event_id=event_id,
        timestamp=reading.timestamp,
        temperature=reading.temperature,
        humidity=reading.humidity,
    )

    event_payload = payload.model_dump(mode="json")

    try:
        logger.info(f"Creating reading and outbox event: event_id={event_id}, temp={reading.temperature}C")
        db.create_reading_and_outbox_event(
            event_id=event_id,
            timestamp=event_payload["timestamp"],
            temperature=event_payload["temperature"],
            humidity=event_payload["humidity"],
            outbox_payload=event_payload,
        )
        logger.info(f"Sensor reading accepted for processing: event_id={event_id}")
        return MessageResponse(
            message="Sensor reading accepted for processing",
            event_id=event_id,
            status="RECEIVED",
        )
    except DuplicateEventError:
        logger.warning(f"Duplicate sensor reading received: event_id={event_id}")
        return MessageResponse(
            message="Sensor reading already accepted",
            event_id=event_id,
            status="RECEIVED",
        )
    except Exception as e:
        logger.error(f"Failed to create sensor reading event: event_id={event_id}, error={str(e)}")
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
        logger.info(f"Retrieving sensor readings: limit={limit}")
        readings = db.get_readings(limit)
        logger.info(f"Retrieved {len(readings)} sensor readings")
        return readings
    except Exception as e:
        logger.error(f"Failed to retrieve sensor readings: {str(e)}")
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
