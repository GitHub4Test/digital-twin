"""
Data models and schemas for sensor data
"""

from pydantic import BaseModel


class SensorReading(BaseModel):
    """Request model for sensor reading submission"""
    timestamp: str
    temperature: float
    humidity: float


class SensorReadingResponse(BaseModel):
    """Response model for sensor reading retrieval"""
    timestamp: str
    temperature: float
    humidity: float


class HealthCheckResponse(BaseModel):
    """Response model for health check endpoint"""
    status: str
    service: str
