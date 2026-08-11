"""
API's for sensor data management
"""

import logging
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Query, Header
from api_gateway.models import (
    SensorReading,
    SensorReadingResponse,
    MessageResponse,
    ErrorResponse,
)
from api_gateway.clients.sensor_client import SensorClient
from api_gateway.rabbitmq.sensor_data_publisher import SensorDataPublisher

logger = logging.getLogger(__name__)

sensorapirouter = APIRouter(prefix="/api/v1/sensors", tags=["sensor-data"])

# API for storing a sensor reading
@sensorapirouter.post(
    "/readings",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Store sensor reading",
    description="Accept a sensor reading and enqueue it for asynchronous processing.",
    responses={
        202: {"description": "Sensor reading accepted for processing"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    }
)
async def create_sensor_reading(
    reading: SensorReading, 
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")
):
    try:
        event_id = idempotency_key or str(uuid4())

        reading.event_id = event_id
        logger.info(f"Creating sensor reading: {reading}")

        # Store the reading data into RabbitMQ
        sensorDataPublisher = SensorDataPublisher()
        sensorDataPublisher.publish_readings(reading)

        logger.info(f"Sensor reading accepted for processing: event_id={event_id}")
        return MessageResponse(
            message="Sensor reading accepted for processing",
            event_id=event_id,
            status="RECEIVED",
        )
    except Exception as e:
        logger.error(f"Failed to create sensor reading event: event_id={event_id}, error={str(e)}")
        raise HTTPException(status_code=500, detail=str(e))    

# API for retrieving sensor readings
@sensorapirouter.get(
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
        sensorClient = SensorClient()
        readings = sensorClient.listReadings(limit)
        logger.info(f"Retrieved {len(readings)} sensor readings")
        return readings
    except Exception as e:
        logger.error(f"Failed to retrieve sensor readings: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")    

# @router.delete(
#     "/readings",
#     response_model=MessageResponse,
#     summary="Delete all sensor readings",
#     description="Remove all sensor readings from the database.",
#     responses={
#         200: {"description": "All sensor readings deleted"},
#         500: {"model": ErrorResponse, "description": "Internal server error"},
#     }
# )
# async def clear_sensor_data():
#     try:
#         db.clear_readings()
#         return MessageResponse(message="All sensor readings cleared successfully")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))