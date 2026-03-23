"""
API routes for sensor data management
"""

from fastapi import APIRouter, HTTPException
from src.models import SensorReading, SensorReadingResponse, HealthCheckResponse
from src.database import Database

router = APIRouter()
db = Database()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    return HealthCheckResponse(
        status="healthy",
        service="backend"
    )


@router.post("/update", response_model=dict)
async def update_sensor(reading: SensorReading):
    """
    Insert sensor reading into database
    
    Args:
        reading: SensorReading object with timestamp, temperature, humidity
    
    Returns:
        Success message
    """
    try:
        result = db.insert_reading(
            reading.timestamp,
            reading.temperature,
            reading.humidity
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data", response_model=list[SensorReadingResponse])
async def get_sensor_data(limit: int = 200):
    """
    Retrieve sensor readings from database
    
    Args:
        limit: Maximum number of records to return (default: 200)
    
    Returns:
        List of sensor readings ordered by timestamp (most recent first)
    """
    try:
        readings = db.get_readings(limit)
        return readings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/data", response_model=dict)
async def clear_sensor_data():
    """Clear all sensor data from database"""
    try:
        result = db.clear_readings()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
